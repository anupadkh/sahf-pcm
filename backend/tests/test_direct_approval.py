from test_review_versions import create,public
from test_workflow import client,auth

def test_moderators_create_and_directly_approve_with_ownership_preserved():
    owner=auth('contributor@pcm.local')
    for index,email in enumerate(['reviewer@pcm.local','admin@pcm.local']):
        moderator=auth(email)
        own,_=create(moderator,'Moderator authored '+str(index),'DIRECT-OWN-'+str(index))
        assert own['created_by']==email
        result=client.post('/api/projects/'+own['id']+'/transition',headers=moderator,json={'action':'publish','note':'Approved directly'})
        assert result.status_code==200 and public(own['id'])
        record,_=create(owner,'Contributor direct approval '+str(index),'DIRECT-OWNER-'+str(index))
        result=client.post('/api/projects/'+record['id']+'/transition',headers=moderator,json={'action':'publish','note':'Checked source'})
        assert result.status_code==200 and result.json()['created_by']=='contributor@pcm.local'
        returned=client.post('/api/projects/'+record['id']+'/transition',headers=moderator,json={'action':'return','note':'Common correction message'})
        assert returned.status_code==200 and returned.json()['comments'][-1]['comment']=='Common correction message'
        assert public(record['id'])
        assert client.post('/api/projects/'+record['id']+'/transition',headers=owner,json={'action':'publish'}).status_code==403
