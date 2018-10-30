from collections import deque
import re

class DiffCommandsError(Exception):
    def __init__(self, message):
        self.message = message

class DiffCommands:
    def __init__(self,file_name = None,data=None):
        if file_name :
            with open(file_name) as file:
                self.commands = file.read()
                commandslist = self.commands.split('\n')
                commandslist.pop()
                original_unchanged = []
                new_unchanged = []
                for c in commandslist:
                    if re.match(r'^([0-9]+,)?[0-9]+d[0-9]+$',c):
                        c = re.split(r'd', c)
                        original_unchanged.append([int(c[0].split(',')[0])-1,int(c[0].split(',')[-1])+1])
                        new_unchanged.append([int(c[1]),int(c[1])+1])
                    elif re.match(r'^[0-9]+a[0-9]+(,[0-9]+)?$',c):
                        c = re.split(r'a', c)
                        original_unchanged.append([int(c[0]),int(c[0])+1])
                        new_unchanged.append([int(c[1].split(',')[0])-1,int(c[1].split(',')[-1])+1])
                    elif re.match(r'^([0-9]+,)?[0-9]+c[0-9]+(,[0-9]+)?$',c):
                        c = re.split(r'c',c)
                        original_unchanged.append([int(c[0].split(',')[0])-1,int(c[0].split(',')[-1])+1])
                        new_unchanged.append([int(c[1].split(',')[0])-1,int(c[1].split(',')[-1])+1])
                    else:
                        raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                if original_unchanged[0][0] != new_unchanged[0][0]:
                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                # print(original_unchanged)
                # print(new_unchanged)
                if all(i[1]-i[0] > 0 for i in original_unchanged) and all(j[1]-j[0] for j in new_unchanged):
                    pass
                else:
                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                original_unchanged_distance = [original_unchanged[x][0]-original_unchanged[x-1][1] for x in range(1,len(original_unchanged))]
                new_unchanged_distance = [new_unchanged[x][0]-new_unchanged[x-1][1] for x in range(1,len(new_unchanged))]
                # print(original_unchanged_distance)
                # print(new_unchanged_distance)
                if all(original_unchanged_distance[i] == new_unchanged_distance[i] and original_unchanged_distance[i]>=0 for i in range(len(original_unchanged_distance))):
                    pass
                else:
                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
        if data:
            self.commands = data
        if not data and not file_name:
            self.commands = None

    def __str__(self):
        if self.commands:
            commands = self.commands.strip('\n')
        else:
            commands = ''
        return commands

class OriginalNewFiles:
    '''
    >>> DiffCommands('diff_1.txt')
    <diff.DiffCommands object at ...>
    >>> diff_1 = DiffCommands('diff_1.txt')
    >>> print(diff_1)
    1,2d0
    3a2
    5c4
    7a7,8
    10d10
    13,16c13,15
    >>> diff_2 = DiffCommands('diff_2.txt')
    >>> print(diff_2)
    1a2
    >>> diff_3 = DiffCommands('diff_3.txt')
    >>> print(diff_3)
    0a1,2
    3,5c5,11
    8d13
    >>> pair_of_files = OriginalNewFiles('file_1_1.txt', 'file_1_2.txt')
    >>> pair_of_files.is_a_possible_diff(diff_1)
    True
    >>> pair_of_files.is_a_possible_diff(diff_2)
    False
    >>> pair_of_files.is_a_possible_diff(diff_3)
    False
    >>> pair_of_files.output_diff(diff_1)
    1,2d0
    < A line to delete: 1
    < A line to delete: 2
    3a2
    > A line to insert: 1
    5c4
    < A line to change: 1
    ---
    > A changed line: 1
    7a7,8
    > A line to insert: 2
    > A line to insert: 3
    10d10
    < A line to delete: 3
    13,16c13,15
    < A line to change: 2
    < A line to change: 3
    < A line to change: 4
    < A line to change: 5
    ---
    > A changed line: 2
    > A changed line: 3
    > A changed line: 4
    >>> pair_of_files.output_unmodified_from_original(diff_1)
    ...
    A line that stays: 1
    A line that stays: 2
    ...
    A line that stays: 3
    A line that stays: 4
    A line that stays: 5
    A line that stays: 6
    ...
    A line that stays: 7
    A line that stays: 8
    ...
    A line that stays: 9
    >>> pair_of_files.output_unmodified_from_new(diff_1)
    A line that stays: 1
    ...
    A line that stays: 2
    ...
    A line that stays: 3
    A line that stays: 4
    ...
    A line that stays: 5
    A line that stays: 6
    A line that stays: 7
    A line that stays: 8
    ...
    A line that stays: 9
    >>> pair_of_files.get_all_diff_commands()
    [<diff.DiffCommands object at ...>]
    >>> diffs = pair_of_files.get_all_diff_commands()
    >>> len(diffs)
    1
    >>> print(diffs[0])
    1,2d0
    3a2
    5c4
    7a7,8
    10d10
    13,16c13,15
    >>> pair_of_files = OriginalNewFiles('file_1_2.txt', 'file_1_1.txt')
    >>> diffs = pair_of_files.get_all_diff_commands()
    >>> len(diffs)
    1
    >>> print(diffs[0])
    0a1,2
    2d3
    4c5
    7,8d7
    10a10
    13,15c13,16
    >>> pair_of_files = OriginalNewFiles('file_1_1.txt', 'file_1_1.txt')
    >>> diffs = pair_of_files.get_all_diff_commands()
    >>> len(diffs)
    1
    >>> print(diffs[0])

    >>> pair_of_files = OriginalNewFiles('file_2_1.txt', 'file_2_2.txt')
    >>> pair_of_files.is_a_possible_diff(diff_1)
    False
    >>> pair_of_files.is_a_possible_diff(diff_2)
    True
    >>> pair_of_files.is_a_possible_diff(diff_3)
    False
    >>> pair_of_files.output_diff(diff_2)
    1a2
    > A line
    >>> pair_of_files.output_unmodified_from_original(diff_2)
    A line
    >>> pair_of_files.output_unmodified_from_new(diff_2)
    A line
    ...
    >>> diffs = pair_of_files.get_all_diff_commands()
    >>> len(diffs)
    2
    >>> print(diffs[0])
    0a1
    >>> print(diffs[1])
    1a2
    >>> pair_of_files = OriginalNewFiles('file_2_2.txt', 'file_2_1.txt')
    >>> diffs = pair_of_files.get_all_diff_commands()
    >>> len(diffs)
    2
    >>> print(diffs[0])
    1d0
    >>> print(diffs[1])
    2d1
    >>> pair_of_files = OriginalNewFiles('file_3_1.txt', 'file_3_2.txt')
    >>> pair_of_files.is_a_possible_diff(diff_1)
    False
    >>> pair_of_files.is_a_possible_diff(diff_2)
    False
    >>> pair_of_files.is_a_possible_diff(diff_3)
    True
    >>> pair_of_files.output_diff(diff_3)
    0a1,2
    > A line to come
    > A line to come
    3,5c5,11
    < A line to go
    < A line to go
    < A line to go
    ---
    > A line to come
    > A line to come
    > Line 1
    > Line 2
    > A line to come
    > A line to come
    > A line to come
    8d13
    < A line to go
    >>> pair_of_files.output_unmodified_from_original(diff_3)
    Line 1
    Line 2
    ...
    Line 3
    Line 4
    ...
    >>> pair_of_files.output_unmodified_from_new(diff_3)
    ...
    Line 1
    Line 2
    ...
    Line 3
    Line 4
    >>> diffs = pair_of_files.get_all_diff_commands()
    >>> len(diffs)
    3
    >>> print(diffs[0])
    0a1,2
    1a4,7
    3,5c9,11
    8d13
    >>> print(diffs[1])
    0a1,2
    3,5c5,11
    8d13
    >>> print(diffs[2])
    0a1,6
    3,5c9,11
    8d13
    >>> pair_of_files = OriginalNewFiles('file_3_2.txt', 'file_3_1.txt')
    >>> diffs = pair_of_files.get_all_diff_commands()
    >>> len(diffs)
    3
    >>> print(diffs[0])
    1,2d0
    4,7d1
    9,11c3,5
    13a8
    >>> print(diffs[1])
    1,2d0
    5,11c3,5
    13a8
    >>> print(diffs[2])
    1,6d0
    9,11c3,5
    13a8
    '''
    def __init__(self, filename1, filename2):
        with open(filename1) as file:
            self.original = [line for line in file]
            # print(self.original)
        with open(filename2) as file:
            self.new = [line for line in file]

    def find_LCS(self):
        self.matrix = [[0 for i in range(len(self.new)+1)] for j in range(len(self.original)+1)]
        self.direction = [[0 for i in range(len(self.new)+1)] for j in range(len(self.original)+1)]
        for i in range(len(self.original)):
            for j in range(len(self.new)):
                if self.original[i] == self.new[j]:
                    self.matrix[i + 1][j + 1] = self.matrix[i][j] + 1
                    self.direction[i + 1][j + 1] = 1  # left_up
                elif self.matrix[i + 1][j] > self.matrix[i][j + 1]:
                    self.matrix[i + 1][j + 1] = self.matrix[i + 1][j]
                    self.direction[i + 1][j + 1] = 2  # left
                elif self.matrix[i + 1][j] < self.matrix[i][j + 1]:
                    self.matrix[i + 1][j + 1] = self.matrix[i][j + 1]
                    self.direction[i + 1][j + 1] = 3  # up
                else:
                    self.matrix[i + 1][j + 1] = self.matrix[i][j + 1]
                    self.direction[i + 1][j + 1] = 4  # left or up
        self.lcslength = self.matrix[-1][-1]
        # print(self.lcslength)
        # for i in self.matrix:
        #     print(i)
        # print()
        # for i in self.direction:
        #     print(i)
        start_points = [(i,j) for i in range(len(self.direction)) for j in range(len(self.direction[0])) if self.matrix[i][j] == 1 and self.direction[i][j]==1]
        end_points = [(i,j) for i in range(len(self.direction)) for j in range(len(self.direction[0])) if self.matrix[i][j] == self.lcslength and self.direction[i][j]==1]
        common_points = [((i,j),self.matrix[i][j]) for i in range(len(self.direction)) for j in range(len(self.direction[0])) if self.direction[i][j] == 1]
        relation = {}
        for i,v1 in common_points:
            relation[i] = []
            for j,v2 in common_points:
                if v2 == v1+1 and j[0]>i[0] and j[1]>i[1]:
                    relation[i].append(j)
        # print(relation)
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

    def get_all_diff_commands_and_results_and_unmodified(self):
        all_diff_commands_and_results_and_unmodified = []
        paths = self.find_LCS()
        for path in paths:
            commands = ''
            results = ''
            position_1 = [0]
            for i in path:
                position_1.append(i[0])
            position_2 = [0]
            for i in path:
                position_2.append(i[1])
            # print(position_1,position_2)
            position_distance_1 = [position_1[i + 1] - position_1[i] for i in range(len(position_1) - 1)]
            position_distance_2 = [position_2[i + 1] - position_2[i] for i in range(len(position_2) - 1)]
            # ==============unmodified====================
            unmodified_1 =''
            for x in range(1,len(position_1)):
                if position_1[x] - position_1[x-1]>1:
                    unmodified_1 += '...\n'+self.original[position_1[x]-1]
                else:
                    unmodified_1 += self.original[position_1[x]-1]
            if position_1[-1] < len(self.original):
                unmodified_1 += '...\n'
            unmodified_2 = ''
            for x in range(1, len(position_2)):
                if position_2[x] - position_2[x - 1] > 1:
                    unmodified_2 += '...\n' + self.new[position_2[x] - 1]
                else:
                    unmodified_2 += self.new[position_2[x]-1]
            if position_2[-1] < len(self.new):
                unmodified_2 += '...\n'
            # =================get all commands and results=================
            for i in range(len(position_distance_1)):
                if position_distance_1[i] > 1 and position_distance_2[i] == 1:
                    if position_distance_1[i] > 2:
                        command = str(position_1[i] + 1) + ',' + str(position_1[i + 1] - 1) + 'd' + str(position_2[i])+'\n'
                        result = command
                        for x in range(position_1[i],position_1[i+1]-1):
                            result += '< '+self.original[x]
                    else:
                        command = str(position_1[i] + 1) + 'd' + str(position_2[i])+'\n'
                        result = command +'< '+ self.original[position_1[i]]
                # ==============add=====================================
                if position_distance_1[i] == 1 and position_distance_2[i] > 1:
                    if position_distance_2[i] > 2:
                        command = str(position_1[i]) + 'a' + str(position_2[i] + 1) + ',' + str(position_2[i + 1] - 1)+'\n'
                        result = command
                        for x in range(position_2[i], position_2[i + 1]-1):
                            result += '> '+self.new[x]
                    else:
                        command = str(position_1[i]) + 'a' + str(position_2[i] + 1)+'\n'
                        result = command + '> ' + self.new[position_2[i]]
                # ===========change==================================
                if position_distance_1[i] > 1 and position_distance_2[i] > 1:
                    if position_distance_1[i] > 2 and position_distance_2[i] > 2:
                        command = str(position_1[i] + 1) + ',' + str(position_1[i + 1] - 1) + 'c' + str(
                            position_2[i] + 1) + ',' + str(position_2[i + 1] - 1)+'\n'
                        result = command
                        for x in range(position_1[i], position_1[i + 1]-1):
                            result += '< '+self.original[x]
                        result += '---\n'
                        for x in range(position_2[i] , position_2[i + 1]-1):
                            result += '> '+self.new[x]
                    elif position_distance_1[i] > 2 and position_distance_2[i] == 2:
                        command = str(position_1[i] + 1) + ',' + str(position_1[i + 1] - 1) + 'c' + str(
                            position_2[i] + 1)+'\n'
                        result = command
                        for x in range(position_1[i] , position_1[i + 1]-1):
                            result += '< ' + self.original[x]
                        result += '---\n'
                        result += '> '+ self.new[position_2[i]]
                    elif position_distance_1[i] == 2 and position_distance_2[i] > 2:
                        command = str(position_1[i] + 1) + 'c' + str(position_2[i] + 1) + ',' + str(
                            position_2[i + 1] - 1)+'\n'
                        result = command + '< '+self.original[position_1[i]]
                        result += '---\n'
                        for x in range(position_2[i], position_2[i + 1]-1):
                            result += '> ' + self.new[x]
                    else:
                        command = str(position_1[i] + 1) + 'c' + str(position_2[i] + 1)+'\n'
                        result = command + '< '+ self.original[position_1[i]]+'---\n'+'> '+self.new[position_2[i]]
                if not (position_distance_1[i] == 1 and position_distance_2[i]) == 1:
                    commands += command
                    results += result
            finalcommand = ''
            finalresult = ''
            if len(self.original) - position_1[-1] > 1 and len(self.new) - position_2[-1] > 1:
                finalcommand = str(position_1[-1] + 1) + ',' + str(len(self.original)) + 'c' + str(position_2[-1] + 1) + ',' + str(
                    len(self.new))+'\n'
                finalresult = finalcommand
                for x in range(position_1[-1] , len(self.original)):
                    finalresult += '< ' + self.original[x]
                finalresult += '---\n'
                for x in range(position_2[-1] , len(self.new)):
                    finalresult += '> ' + self.new[x]
            if len(self.original) - position_1[-1] == 1 and len(self.new) - position_2[-1] > 1:
                finalcommand = str(len(self.original)) + 'c' + str(position_2[-1] + 1) + ',' + str(len(self.new))+'\n'
                finalresult = finalcommand + '< '+self.original[len(self.original)-1]
                finalresult += '---\n'
                for x in range(position_2[-1] , len(self.new)):
                    finalresult += '> ' + self.new[x]
            if len(self.original) - position_1[-1] > 1 and len(self.new) - position_2[-1] == 1:
                finalcommand = str(position_1[-1] + 1) + ',' + str(len(self.original)) + 'c' + str(len(self.new))+'\n'
                finalresult = finalcommand
                for x in range(position_1[-1], len(self.original)):
                    finalresult += '< ' + self.original[x]
                finalresult += '---\n'
                finalresult += '> '+self.new[len(self.new)-1]
            if len(self.original) - position_1[-1] == 1 and len(self.new) - position_2[-1] == 1:
                finalcommand = str(len(self.original)) + 'c' + str(len(self.new))+'\n'
                finalresult = finalcommand + '< ' + self.original[len(self.original) - 1]+'---\n'+'> '+self.new[len(self.new)-1]
            if len(self.original) == position_1[-1] and len(self.new) - position_2[-1] > 1:
                finalcommand = str(len(self.original)) + 'a' + str(position_2[-1] + 1) + ',' + str(len(self.new))+'\n'
                finalresult = finalcommand
                for x in range(position_2[-1], len(self.new)):
                    finalresult += '>' + self.new[x]
            if len(self.original) == position_1[-1] and len(self.new) - position_2[-1] == 1:
                finalcommand = str(len(self.original)) + 'a' + str(len(self.new))+'\n'
                finalresult = finalcommand + '> ' + self.new[-1]
            if len(self.original) - position_1[-1] > 1 and len(self.new) == position_2[-1]:
                finalcommand = str(position_1[-1] + 1) + ',' + str(len(self.original)) + 'd' + str(len(self.new))+'\n'
                finalresult = finalcommand
                for x in range(position_1[-1], len(self.original)):
                    result += '<' + self.original[x]
            if len(self.original) - position_1[-1] == 1 and len(self.new) == position_2[-1]:
                finalcommand = str(len(self.original)) + 'd' + str(len(self.new))+'\n'
                finalresult = finalcommand + '< ' + self.original[-1]
            if finalcommand:
                commands += finalcommand
                results += finalresult
            # print(commands)
            # print(results)
            all_diff_commands_and_results_and_unmodified.append([commands,results.strip('\n'),unmodified_1.strip('\n'),unmodified_2.strip('\n')])
        # print(all_diff_commands_and_results_and_unmodified[0])
        return all_diff_commands_and_results_and_unmodified

    def get_all_diff_commands(self):
        all_commands = [x[0].strip('\n') for x in self.get_all_diff_commands_and_results_and_unmodified()]
        all_commands.sort()
        all_commands_object = []
        for i in all_commands:
            command_object = DiffCommands(data = i)
            all_commands_object.append(command_object)
        return all_commands_object

    def is_a_possible_diff(self,diff):
        all_commands = [x[0] for x in self.get_all_diff_commands_and_results_and_unmodified()]
        if diff.commands in all_commands:
            return True
        else:
            return False

    def output_diff(self,diff):
        for i in self.get_all_diff_commands_and_results_and_unmodified():
            if diff.commands == i[0]:
                print(i[1])

    def output_unmodified_from_original(self,diff):
        for i in self.get_all_diff_commands_and_results_and_unmodified():
            if diff.commands == i[0]:
                print(i[2])

    def output_unmodified_from_new(self,diff):
        for i in self.get_all_diff_commands_and_results_and_unmodified():
            if diff.commands == i[0]:
                print(i[3])



if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
    p = OriginalNewFiles('file_4_1.txt','file_4_2.txt')
    # paths = p.find_LCS()
    # for i in paths:
    #     print(i)
    diffs = p.get_all_diff_commands()
    print(len(diffs))
    print(diffs[0])
    # for i in range(len(diffs)):
    #     print(diffs[i])
    diff_1 = DiffCommands('diff_2.txt')
    # print(diff_1)
    # print()
    # print(p.is_a_possible_diff(diff_1))
    # print()
    # print(p.output_diff(diff_1))
    # print()
    print(p.output_unmodified_from_original(diff_1))
    print('-'*20)
    print(p.output_unmodified_from_new(diff_1))
    # print()
    # print(p.output_unmodified_from_new(diff_1))







