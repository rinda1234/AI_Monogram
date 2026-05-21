def generate_domain(hint, length):
    """
    주어진 힌트(hint)와 줄의 길이(length)를 만족하는 모든 가능한 배치(도메인)를 생성합니다.
    예: hint=[2, 1], length=5 ->
        [ [1, 1, 0, 1, 0],
          [1, 1, 0, 0, 1],
          [0, 1, 1, 0, 1] ]
    """
    if not hint or hint == [0]:
        return [[0] * length]
    
    def backtrack(hint_idx, current_len):
        if hint_idx == len(hint):
            return [(length - current_len) * [0]]
        
        results = []
        rem_hints = hint[hint_idx:]
        # 남은 힌트들을 배치하기 위해 필요한 최소 칸 수 
        # (각 힌트 길이의 합 + 힌트 사이의 최소 여백 1칸씩)
        min_required = sum(rem_hints) + len(rem_hints) - 1
        
        # 현재 힌트 앞에 올 수 있는 0(빈칸)의 최대 개수
        max_zeros = length - current_len - min_required
        
        for zeros in range(max_zeros + 1):
            # 빈칸(0) zeros개와 칠해진 칸(1) hint[hint_idx]개
            prefix = [0] * zeros + [1] * hint[hint_idx]
            
            # 마지막 힌트가 아니면 서로 구분하기 위해 최소 1개의 빈칸(0)이 필요
            if hint_idx < len(hint) - 1:
                prefix += [0]
                
            for suffix in backtrack(hint_idx + 1, current_len + len(prefix)):
                results.append(prefix + suffix)
                
        return results

    return backtrack(0, 0)

def print_board(rows_domain_assignment):
    """
    가로(Row) 변수들에 할당된 값을 기반으로 보드를 출력합니다.
    rows_domain_assignment: 각 가로줄의 최종 결정된 값 (예: [1, 1, 0, 1, 0])이 담긴 리스트.
    """
    if not rows_domain_assignment:
        print("Empty board.")
        return
        
    for row in rows_domain_assignment:
        line = ""
        for cell in row:
            if cell == 1:
                line += "██"
            else:
                line += ".."
        print(line)
