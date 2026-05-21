import time
from typing import Dict, List, Optional, Any

class TimeoutException(Exception):
    """지정된 시간을 초과했을 때 탐색을 강제 종료하기 위한 에러 클래스입니다."""
    pass

def backtracking_search(csp: Any, assignment: Optional[Dict[str, List[int]]] = None, start_time: Optional[float] = None, timeout: Optional[float] = None) -> Optional[Dict[str, List[int]]]:
    """
    [Step 2] 순수 백트래킹(Backtracking Search) 알고리즘 적용
    
    도메인 축소를 위한 논리 추론(Inference) 과정 없이, 단순히 변수에 도메인을 대입하고 재귀적으로 탐색해 내려가는 심층 우선 탐색(DFS) 형태의 백트래킹을 구현합니다.
    
    지시사항:
    1. assignment는 현재까지 확정된 변수들을 담는 딕셔너리입니다. (예: {'R0': [1,0,1], 'C0': [1,1,0], ...})
    2. 모든 변수가 할당되었다면 assignment를 즉각 반환하여 종료합니다.
    3. 아직 할당되지 않은 변수들 중 별도의 휴리스틱 계산 없이 단순히 첫 번째 변수(unassigned[0])를 맹목적으로 선택하십시오.
    4. 선택된 변수가 가질 수 있는 도메인(csp.domains)의 배열 패턴들을 하나씩 할당해 보며, 기존의 assignment 변수들과 충돌(is_consistent)이 나지 않는다면 재귀적으로 backtracking_search를 호출합니다.
    5. start_time 및 timeout이 설정된 경우 시간 제한 안에 탐색하지 못할 시 TimeoutException을 발생시켜 알고리즘 효율의 한계를 증명합니다.
    
    Returns:
        최종 퍼즐 정답 딕셔너리, 만약 해답이 존재하지 않는 길이라면 None
    """
    if start_time is not None and timeout is not None:
        if time.time() - start_time > timeout:
            raise TimeoutException("Timeout")
            
    if assignment is None:
        assignment = {}
        
    # ==========================
    # 아래에 코드를 작성하세요.
    # ==========================
    return None
