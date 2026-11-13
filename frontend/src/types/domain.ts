export interface User{id:number;email:string;name:string;role:'admin'|'analyst'|'viewer'}
export interface Study{id:number;code:string;name:string;protocol:string;source_file:string}
export interface Treatment{id:number;study_id?:number;code:string;name:string;process_note:string}
export interface Reading{id:number;study_id?:number;treatment_id:number;specimen_code:string;grade:number;source_note:string;pooled_rank?:number}
export interface Group extends Treatment{n:number;rank_sum:number;mean_rank:number;median_lower:number;median_upper:number;grade_counts:Record<string,number>}
export interface Pair{i:number;j:number;left_code:string;right_code:string;left_name:string;right_name:string;mean_rank_difference:number;standard_error:number;z:number;p_raw_asymptotic:number;p_holm:number;reject:boolean}
export interface Snapshot{study:Study;treatments:Treatment[];readings:Reading[]}
export interface Result{n:number;k:number;h_raw:number;h:number;df:number;p_asymptotic:number;p_underflow:boolean;tie_term:number;tie_correction:number;dunn_variance:number;ties:{grade:number;count:number;average_rank:number;term:number}[];groups:Group[];pairs:Pair[];ranked_readings:Reading[];alpha:number;omnibus_reject:boolean;family_size:number;fingerprint:string;p_method:string;snapshot:Snapshot}
export interface Run{id:number;study_id:number;name:string;alpha:number;status:'queued'|'running'|'completed'|'failed';snapshot:Snapshot;result:Result;error:string;created_at:string}
export interface Note{id:number;name:string;run_id:number;rationale:string;status:'draft'|'approved'|'rejected';reviewer_note:string;reviewed_by:string;created_at:string}
