from collections import deque
with open('file_1_1.txt') as file:
    original = [line for line in file]
with open('file_1_2.txt') as file:
    new = [line for line in file]

# print(original)
# print(new)


def LCS(original,new):
    matrix = [[0 for i in range(len(new) + 1)] for j in range(len(original) + 1)]
    direction = [[0 for i in range(len(new) + 1)] for j in range(len(original) + 1)]
    for i in range(len(original)):
        for j in range(len(new)):
            if original[i] == new[j]:
                matrix[i+1][j+1] = matrix[i][j] + 1
                direction[i+1][j+1] = 1  # left_up
            elif matrix[i+1][j] > matrix[i][j+1]:
                matrix[i+1][j+1] = matrix[i+1][j]
                direction[i+1][j+1] = 2  # left
            elif matrix[i+1][j] < matrix[i][j+1]:
                matrix[i+1][j+1] = matrix[i][j+1]
                direction[i+1][j+1] = 3     # up
            else:
                matrix[i+1][j+1] = matrix[i][j+1]
                direction[i+1][j+1] = 4   # left or up
    for i in matrix:
        print(i)
    print()
    for j in direction:
        print(j)
    lcs_length = matrix[-1][-1]
    start_points = [(i,j) for i in range(len(direction)) for j in range(len(direction[0])) if matrix[i][j] == 1 and direction[i][j]==1]
    end_points = [(i,j) for i in range(len(direction)) for j in range(len(direction[0])) if matrix[i][j] == lcs_length and direction[i][j]==1]
    common_points = [((i,j),matrix[i][j]) for i in range(len(direction)) for j in range(len(direction[0])) if direction[i][j] == 1]
    relation = {}
    for i,v1 in common_points:
        relation[i] = []
        for j,v2 in common_points:
            if v2 == v1+1 and j[0]>i[0] and j[1]>i[1]:
                relation[i].append(j)
    print(relation)
    stack = deque()
    paths = []
    for i in start_points:
        stack.append((i,[i]))
    while stack:
        node, path = stack.pop()
        if node in end_points:
            paths.append(path)
        if node in relation:
            for i in relation[node]:
                stack.appendleft((i,path + [i]))
    return paths

def get_all_diff_commands(paths,a,b):
    all_diff_commands = []
    for path in paths:
        commands = ''
        position_1 = [0]
        for i in path:
            position_1.append(i[0])
        position_2 = [0]
        for i in path:
            position_2.append(i[1])
        # print(position_1,position_2)
        position_distance_1 = [position_1[i + 1] - position_1[i] for i in range(len(position_1) - 1)]
        position_distance_2 = [position_2[i + 1] - position_2[i] for i in range(len(position_2) - 1)]
        for i in range(len(position_distance_1)):
            if position_distance_1[i] > 1 and position_distance_2[i] == 1:
                if position_distance_1[i] > 2:
                    command = str(position_1[i]+1)+',' + str(position_1[i+1] - 1) + 'd'+str(position_2[i])+'\n'
                else:
                    command = str(position_1[i]+1)+'d'+str(position_2[i])+'\n'
            if position_distance_1[i] == 1 and position_distance_2[i] > 1:
                if position_distance_2[i] > 2:
                    command = str(position_1[i])+'a'+str(position_2[i]+1)+',' + str(position_2[i+1] - 1)+'\n'
                else:
                    command = str(position_1[i])+'a'+str(position_2[i]+1)+'\n'
            if position_distance_1[i] > 1 and position_distance_2[i] > 1:
                if position_distance_1[i] > 2 and position_distance_2[i] > 2:
                    command = str(position_1[i]+1)+',' + str(position_1[i+1]-1) + 'c'+str(position_2[i]+1)+',' + str(position_2[i+1]-1)+'\n'
                elif position_distance_1[i] > 2 and position_distance_2[i] == 2:
                    command = str(position_1[i]+1)+',' + str(position_1[i+1] - 1) + 'c'+str(position_2[i]+1)+'\n'
                elif position_distance_1[i] == 2 and position_distance_2[i] > 2:
                    command = str(position_1[i]+1)+'c'+str(position_2[i]+1)+',' + str(position_2[i+1] - 1)+'\n'
                else :
                    command = str(position_1[i]+1)+'c'+str(position_2[i]+1)+'\n'
            if not(position_distance_1[i] == 1 and position_distance_2[i]) == 1:
                commands += command
        finalcommand = ''
        if len(a)-position_1[-1]>1 and len(b)-position_2[-1]>1:
            finalcommand = str(position_1[-1]+1)+','+str(len(a))+'c'+str(position_2[-1]+1)+','+str(len(b))+'\n'
        if len(a)-position_1[-1]==1 and len(b)-position_2[-1]>1:
            finalcommand = str(len(a)) + 'c' + str(position_2[-1] + 1) + ',' + str(len(b))+'\n'
        if len(a)-position_1[-1]>1 and len(b)-position_2[-1]==1:
            finalcommand = str(position_1[-1]+1)+','+str(len(a))+'c'+str(len(b))+'\n'
        if len(a)-position_1[-1]==1 and len(b)-position_2[-1]==1:
            finalcommand = str(len(a))+'c'+str(len(b))+'\n'
        if len(a) == position_1[-1] and len(b)-position_2[-1]>1:
            finalcommand = str(len(a))+'a'+str(position_2[-1]+1)+','+str(len(b))+'\n'
        if len(a) == position_1[-1] and len(b)-position_2[-1]==1:
            finalcommand = str(len(a))+'a'+str(len(b))+'\n'
        if len(a)-position_1[-1]>1 and len(b)==position_2[-1]:
            finalcommand = str(position_1[-1]+1)+','+str(len(a))+'d'+str(len(b))+'\n'
        if len(a)-position_1[-1]==1 and len(b)==position_2[-1]:
            finalcommand = str(len(a))+'d'+str(len(b))+'\n'
        if finalcommand:
            commands += finalcommand
        all_diff_commands.append(commands)
        # print(all_diff_commands)
    return all_diff_commands

# a = 'ABCBDAB'
# b = 'BDCABA'
a = 'ABCCCDEC'
b = 'FFABFFABFFFDE'
# a = 'A'
# b = 'AA'
paths = LCS(a,b)
for i in paths:
    print(i)
diff = get_all_diff_commands(paths,a,b)
for i in diff:
    print(i)


