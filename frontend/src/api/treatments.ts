import {request,post} from './client';import type {Treatment} from '../types/domain';export const list=(study_id:number)=>request<Treatment[]>('/treatments'+`?study_id=${study_id}`);export const create=(data:unknown)=>post<Treatment>('/treatments',data);
export const update=(id:number,data:unknown)=>request<Treatment>('/treatments/'+id,{method:'PUT',body:JSON.stringify(data)});
