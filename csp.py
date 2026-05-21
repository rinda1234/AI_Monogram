import time
from typing import List, Dict, Any, Union
from steps.step1_init import NonogramCSP
from steps.step2_backtrack import backtracking_search, TimeoutException
from steps.step3_revise import revise
from steps.step4_ac3 import ac3

def solve_nonogram(row_hints: List[List[int]], col_hints: List[List[int]], algo: str = "step4") -> Dict[str, Any]:
    """
    [수정 금지] 알고리즘을 모드(algo)별로 실행할 수 있는 메인 파이프라인.
    """
    csp = NonogramCSP(row_hints, col_hints)
    
    if algo == "step1":
        # Step 1: Setup Variables, Domains, Constraints check
        domain_count = sum(len(csp.domains.get(v, [])) for v in csp.variables)
        domain_details = {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}
                
        return {
            "status": "STEP1_DONE", 
            "domains": domain_count, 
            "domain_details": domain_details,
            "variables_count": len(csp.variables),
            "constraints_count": csp.M * csp.N
        }
        
    elif algo == "step2":
        # Step 2: Pure Backtracking
        try:
            assignment = backtracking_search(csp, start_time=time.time(), timeout=15.0)
            if assignment is None: return {"status": "NO_SOLUTION", "domain_details": {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}}
            return {"status": "SOLVED", "assignment": assignment, "domain_details": {v: {"count": 1, "samples": [assignment.get(v, [])]} for v in csp.variables}}
        except TimeoutException:
            return {"status": "TIMEOUT", "msg": "백트래킹 연산 15초 시간초과. 효율적인 알고리즘이 필요합니다.", "domain_details": {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}}
            
    elif algo == "step3":
        # Step 3: Run revise once for all edges + Backtracking
        for r_var in [v for v in csp.variables if v.startswith('R')]:
            for c_var in [v for v in csp.variables if v.startswith('C')]:
                revise(csp, r_var, c_var)
                revise(csp, c_var, r_var)
        
        if any(len(csp.domains.get(v, [])) == 0 for v in csp.variables):
            return {"status": "NO_SOLUTION", "domain_details": {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}}
            
        try:
            assignment = backtracking_search(csp, start_time=time.time(), timeout=15.0)
            if assignment is None: return {"status": "NO_SOLUTION", "domain_details": {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}}
            return {"status": "SOLVED", "assignment": assignment, "domain_details": {v: {"count": 1, "samples": [assignment.get(v, [])]} for v in csp.variables}}
        except TimeoutException:
            return {"status": "TIMEOUT", "msg": "Filtering 1회 적용 후 백트래킹 15초 초과. 완벽한 글로벌 AC-3가 필요합니다.", "domain_details": {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}}
            
    elif algo == "step4" or algo is None:
        # Step 4: True AC-3 + Backtracking
        if not ac3(csp):
            return {"status": "NO_SOLUTION", "domain_details": {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}}
            
        if all(len(csp.domains.get(v, [])) == 1 for v in csp.variables):
            assignment = {v: csp.domains.get(v, [])[0] for v in csp.variables}
            return {"status": "SOLVED", "assignment": assignment, "domain_details": {v: {"count": 1, "samples": [assignment.get(v, [])]} for v in csp.variables}}
        else:
            try:
                assignment = backtracking_search(csp, start_time=time.time(), timeout=15.0)
                if assignment is None: return {"status": "NO_SOLUTION", "domain_details": {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}}
                return {"status": "SOLVED", "assignment": assignment, "domain_details": {v: {"count": 1, "samples": [assignment.get(v, [])]} for v in csp.variables}}
            except TimeoutException:
                return {"status": "TIMEOUT", "msg": "최적화 실패 (Timeout)", "domain_details": {v: {"count": len(csp.domains.get(v, [])), "samples": csp.domains.get(v, [])[:10]} for v in csp.variables}}
