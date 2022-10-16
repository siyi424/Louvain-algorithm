def solveSudoku(input):
    board = input
    # decide which gid 
    def cal_gid(i, j) -> int:
        return 3 * (i // 3) + j // 3

    def get_leftNums(i, j):
        Nums = [str(n) for n in range(1, 10)]
        Rows = board[i]
        Cols = []
        gid = cal_gid(i, j)
        Grid = []

        for x in range(9):
            Cols.append(board[x][j])
            for y in range(9):
                if cal_gid(x, y) == gid:
                    Grid.append(board[x][y])

        leftNums = list(set(Nums) - set(Rows) - set(Cols) - set(Grid))
        return leftNums

    def get_next_pos(i, j):
        for x in range(i, 9):
            for y in range(9):
                if x == i and y <= j:
                    continue
                if board[x][y] == '0':
                    return x, y
        return -1, -1
    
    def get_start_pos():
        for x in range(9):
            for y in range(9):
                if board[x][y] == '0':
                    return x, y
        return -1, -1
    
    def dfs(i, j):
        leftNums = get_leftNums(i, j)

        for n in leftNums:
            board[i][j] = n
            nx, ny = get_next_pos(i, j)
            if ny == -1:
                return True
            else:
                end = dfs(nx, ny)
                if end:
                    return True
                board[nx][ny] = '0'
    
    sx, sy = get_start_pos()
    dfs(sx, sy)
    return board

board = [
    ['3', '0', '6', '5', '0', '8', '4', '0', '0'],
    ['5', '2', '0', '0', '0', '0', '0', '0', '0'],
    ['0', '8', '7', '0', '0', '0', '0', '3', '1'],
    ['0', '0', '3', '0', '1', '0', '0', '8', '0'],
    ['9', '0', '0', '8', '6', '3', '0', '0', '5'],
    ['0', '5', '0', '0', '9', '0', '6', '0', '0'],
    ['1', '3', '0', '0', '0', '0', '2', '5', '0'],
    ['0', '0', '0', '0', '0', '0', '0', '7', '4'],
    ['0', '0', '5', '2', '0', '6', '3', '0', '0']
]


# import time
# time_start = time.time()
output = solveSudoku(board)
# time_end = time.time()

# delta_time = time_end - time_end

# print('解数独时间：', delta_time)
for row in output:
    print(row)