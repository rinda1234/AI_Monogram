from typing import List, Dict
from utils.nonogram_utils import generate_domain

class NonogramCSP:
    """
    Nonogram 퍼즐을 Constraint Satisfaction Problem (CSP) 형태로 정의하는 클래스입니다.
    """
    row_hints: List[List[int]] # 각 행에 대한 힌트 (예: [[3], [1, 1], [2]])
    col_hints: List[List[int]] # 각 열에 대한 힌트 (예: [[2], [1, 1], [3]])
    M: int # 행의 수
    N: int # 열의 수
    variables: List[str] # 퍼즐의 변수 리스트 (예: ['R0', 'R1', 'C0', 'C1'])
    domains: Dict[str, List[List[int]]] # 각 변수에 대한 도메인 (예: {'R0': [[1, 1, 1], [0, 1, 1]], 'C0': [[1, 0, 1], [0, 1, 0]]})

    def __init__(self, row_hints: List[List[int]], col_hints: List[List[int]]) -> None:
        """
        [Step 1-1] 변수 및 도메인 초기화
        
        시스템이 퍼즐을 CSP로 이해할 수 있도록 변수(self.variables)와 초기 도메인(self.domains)을 구축합니다.
        
        지시사항:
        1. 가로축 변수명은 'R0', 'R1', ... 배열 형식으로 리스트에 추가합니다.
        2. 세로축 변수명은 'C0', 'C1', ... 배열 형식으로 리스트에 추가합니다.
        3. utils/nonogram_utils.py에 구현된 'generate_domain(hint, length)'를 호출하여 해당 행/열의 초기 가능한 모든 배열 경우의 수를 확보하고 딕셔너리에 매핑하세요.
        """
        self.row_hints = row_hints
        self.col_hints = col_hints
        self.M = len(row_hints) # 행의 수
        self.N = len(col_hints) # 열의 수
        
        self.variables = []
        self.domains = {}
        
        # ==========================
        # 아래에 코드를 작성하세요.
        # ==========================
        
        # 가로축 변수 및 도메인 초기화
        for i in range(self.M):
            r_var = "R" + str(i)
            self.variables.append(r_var)
            self.domains[r_var] = generate_domain(self.row_hints[i], self.N)
        
        # 세로축 변수 및 도메인 초기화
        for i in range(self.N):
            c_var = "C" + str(i)
            self.variables.append(c_var)
            self.domains[c_var] = generate_domain(self.col_hints[i], self.M)    
        
        pass

    def is_consistent(self, r_var: str, r_val: List[int], c_var: str, c_val: List[int]) -> bool:
        """
        [Step 1-2] 제약 조건(Constraints) 일관성 검사 함수
        
        수직으로 교차되는 두 변수(행렬) 간에 모순이 발생하지 않는지 판단합니다.
        
        지시사항:
        - r_var(예: "R2"), c_var(예: "C3")의 값 상태인 r_val과 c_val의 논리적 교차 지점(픽셀)이 완전히 동일한지 확인하여야 합니다.
        - 파라미터 순서가 뒤바뀌어 들어오는 경우(예: r_var가 'C'로 시작하는 경우)에도 정상적으로 비교 및 처리될 수 있도록 예외 처리를 권장합니다.
        
        Returns:
            bool: 두 도메인 배열 패턴이 해당 교차점에서 충돌 없이 일치하면 True, 충돌하면 False
        """
        # ==========================
        # 아래에 코드를 작성하세요.
        # ==========================

        # 예외 처리: 파라미터가 뒤바뀌어 들어오는 경우 둘을 교환
        if r_var.startswith("C") and c_var.startswith("R"):
            r_var, c_var = c_var, r_var
            r_val, c_val = c_val, r_val
        
        # 교차점의 인덱스 계산
        r = int(r_var[1:])
        c = int(c_var[1:])

        # 교차점 충돌 검사
        if r_val[c] == c_val[r]:
            return True
        else:
            return False
