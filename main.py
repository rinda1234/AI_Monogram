from csp import solve_nonogram
import time
from utils.puzzles import PUZZLES

if __name__ == "__main__":
    print("AI Assignment 3: CSP Nonogram Solver")
    print("=====================================")

    total_time = 0
    passed = 0
    
    for name, data in PUZZLES.items():
        print(f"\n[{name}]")
        start = time.time()
        # 1~4 단계 모드를 바꿔가며 테스트해볼 수 있습니다. 
        # algo="step1", "step2", "step3", "step4"
        ans = solve_nonogram(data["r"], data["c"], algo="step4")
        dt = time.time() - start
        total_time += dt
        
        if ans and ans.get("status") == "SOLVED":
            passed += 1
            print(f"-> Solved in {dt:.4f} sec")
        else:
            msg = ans.get("msg", "해답 없음") if ans else "해답 없음"
            print(f"-> NO SOLUTION or FAILED ({msg}) in {dt:.4f} sec")
            
    print("\n=====================================")
    print(f"Final Result: {passed} / {len(PUZZLES)} Puzzles Solved")
    print(f"Total Time: {total_time:.4f} sec")
    print("=====================================")
