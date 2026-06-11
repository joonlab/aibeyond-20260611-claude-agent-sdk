def fibonacci(n):
    """0부터 시작하는 피보나치 수열의 처음 n개를 반환한다.
    예: fibonacci(5) -> [0, 1, 1, 2, 3]
    """
    seq = [0, 1]
    for i in range(2, n):
        seq.append(seq[i - 1] + seq[i - 2])
    return seq  # n=1 일 때 [0, 1] 로 2개를 반환하는 버그


if __name__ == "__main__":
    print(fibonacci(5))
