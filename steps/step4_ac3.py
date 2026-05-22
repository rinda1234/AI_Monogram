from typing import Any
from collections import deque
from steps.step3_revise import revise

def ac3(csp: Any) -> bool:
    """
    [Step 4] 제약 전파 결합 논리 추론 최적화 (AC-3)
    
    큐(Queue)를 활용하여 수정 사항 발생 파동을 전체 보드망으로 연쇄 전파(Propagation)함으로써 전역적인 일관성(Arc Consistency)을 달성합니다.
    
    지시사항:
    1. Queue 자료구조를 생성하고, 초기 세팅으로 상호 교차하는 모든 엣지 쌍 (R_i, C_j)와 (C_j, R_i)를 통째로 집어넣습니다.
    2. Queue가 완전히 빌 때까지 원소를 하나씩 pop(xi, xj)하며, 미리 구현해둔 revise(csp, xi, xj) 함수를 호출하여 필터링을 시도합니다.
    3. 만약 revise 호출 결과로 xi의 도메인이 깎여나갔다면(True 반환 시), xi 상태가 변했으므로 xi와 교차하는 다른 모든 이웃 변수들(xk)에 파급 효과가 있을 수 있습니다.
       이에 대한 검증을 위해 (xk, xi) 쌍들을 다시 Queue에 집어넣고 재심사 대기열에 올립니다.
    4. 위 전파(Propagation) 과정 중 발생한 연쇄작용으로 인해 찰나에 특정 변수의 도메인 길이가 0이 되어 버린다면, 이 퍼즐의 경로 자체가 치명적 모순임을 나타내므로 즉각 False를 반환합니다.
    5. 교착 상태 없이 큐가 무사히 비워졌다면 최종적으로 True를 반환합니다.
    
    Returns:
        bool: Arc Consistency가 문제 없이 확보되었다면 True, 논리적 결함(도메인 고갈)이 발생했다면 False
    """
    # ==========================
    # 아래에 코드를 작성하세요.
    # ==========================
    # 큐 초기화
    queue = deque()
    for R_i in [v for v in csp.variables if v.startswith('R')]:
        for C_j in [v for v in csp.variables if v.startswith('C')]:
            # 상호교차하는 모든 엣지쌍 큐에 삽입.
            queue.append((R_i, C_j))
            queue.append((C_j, R_i))
    
    # 큐가 빌때까지 반복
    while queue:
        # 큐에서 원소 하나씩 pop
        xi, xj = queue.popleft()
        # 필터링
        if revise(csp, xi, xj):
            # xi 의 domain 길이가 0인지 체크
            if not csp.domains[xi]:
                return False 
            # xi의 도메인이 깍여나갔다면 재심사 대기열 올리기
            for xk in [v for v in csp.variables if v[0] != xi[0] and v != xj]: # xi와 교차하는 다른 모든 이웃 변수들(xk)
                if (xk, xi) not in queue:
                    queue.append((xk, xi))        

    return True
