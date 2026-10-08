import {inject} from '@angular/core';
import {CanActivateFn,Router} from '@angular/router';
import {AuthService,rolePath} from './auth.service';
export const roleGuard:CanActivateFn=async(route)=>{
  const auth=inject(AuthService),router=inject(Router);await auth.restore();
  const user=auth.user();
  if(!user)return router.createUrlTree(['/login']);
  return user.role===route.data['area']?true:router.parseUrl(rolePath(user.role));
};
