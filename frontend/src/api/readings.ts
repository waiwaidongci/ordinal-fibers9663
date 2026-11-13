import {request,post} from './client';import type {Reading} from '../types/domain';export const list=(study_id:number)=>request<Reading[]>('/readings'+`?study_id=${study_id}`);export const create=(data:unknown)=>post<Reading>('/readings',data);
export const update=(id:number,data:unknown)=>request<Reading>('/readings/'+id,{method:'PUT',body:JSON.stringify(data)});
