from collections import deque
import re
from copy import deepcopy

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
                if commandslist:
                    original_unchanged = []
                    new_unchanged = []
                    for c in commandslist:
                        if re.match(r'^([0-9]+,)?[0-9]+d[0-9]+$',c):
                            c = re.split(r'd', c)
                            if len(c[0].split(',')) == 2:
                                if int(c[0].split(',')[0]) >= int(c[0].split(',')[-1]):
                                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                            original_unchanged.append([int(c[0].split(',')[0])-1,int(c[0].split(',')[-1])+1])
                            new_unchanged.append([int(c[1]),int(c[1])+1])
                        elif re.match(r'^[0-9]+a[0-9]+(,[0-9]+)?$',c):
                            c = re.split(r'a', c)
                            if len(c[0].split(',')) == 2:
                                if int(c[1].split(',')[0]) >= int(c[1].split(',')[-1]):
                                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                            original_unchanged.append([int(c[0]),int(c[0])+1])
                            new_unchanged.append([int(c[1].split(',')[0])-1,int(c[1].split(',')[-1])+1])
                        elif re.match(r'^([0-9]+,)?[0-9]+c[0-9]+(,[0-9]+)?$',c):
                            c = re.split(r'c',c)
                            if len(c[0].split(',')) == 2:
                                if int(c[0].split(',')[0]) >= int(c[0].split(',')[-1]):
                                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                            if len(c[1].split(',')) == 2:
                                if int(c[1].split(',')[0]) >= int(c[1].split(',')[-1]):
                                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                            original_unchanged.append([int(c[0].split(',')[0])-1,int(c[0].split(',')[-1])+1])
                            new_unchanged.append([int(c[1].split(',')[0])-1,int(c[1].split(',')[-1])+1])
                        else:
                            raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                    if original_unchanged[0][0] != new_unchanged[0][0]:
                        raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                    original_unchanged_distance = [original_unchanged[x][0]-original_unchanged[x-1][1] for x in range(1,len(original_unchanged))]
                    new_unchanged_distance = [new_unchanged[x][0]-new_unchanged[x-1][1] for x in range(1,len(new_unchanged))]
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

    def __init__(self, filename1, filename2):
        with open(filename1) as file:
            self.original = [line for line in file]
            self.original.append('')
            # print(self.original)
        with open(filename2) as file:
            self.new = [line for line in file]
            self.new.append('')

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
        start_points = [(i,j) for i in range(len(self.direction)) for j in range(len(self.direction[0])) if self.matrix[i][j] == 1 and self.direction[i][j]==1]
        end_points = [(i,j) for i in range(len(self.direction)) for j in range(len(self.direction[0])) if self.matrix[i][j] == self.lcslength and self.direction[i][j]==1]
        common_points = [((i,j),self.matrix[i][j]) for i in range(len(self.direction)) for j in range(len(self.direction[0])) if self.direction[i][j] == 1]
        relation = {}
        for i,v1 in common_points:
            relation[i] = []
            for j,v2 in common_points:
                if v2 == v1+1 and j[0]>i[0] and j[1]>i[1]:
                    relation[i].append(j)
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
            position_1_u = deepcopy(position_1)
            position_1.append(len(self.original)+1)
            position_2 = [0]
            for i in path:
                position_2.append(i[1])
            position_2_u = deepcopy(position_2)
            # print(position_2_u)
            position_2.append(len(self.new)+1)
            position_distance_1 = [position_1[i + 1] - position_1[i] for i in range(len(position_1) - 1)]
            position_distance_2 = [position_2[i + 1] - position_2[i] for i in range(len(position_2) - 1)]
            # ==============unmodified====================
            unmodified_1 =''
            for x in range(1,len(position_1_u)):
                if position_1_u[x] - position_1_u[x-1]>1:
                    unmodified_1 += '...\n'+self.original[position_1_u[x]-1]
                else:
                    unmodified_1 += self.original[position_1_u[x]-1]

            unmodified_2 = ''
            for x in range(1, len(position_2_u)):
                if position_2_u[x] - position_2_u[x - 1] > 1:
                    unmodified_2 += '...\n' + self.new[position_2_u[x] - 1]
                else:
                    unmodified_2 += self.new[position_2_u[x]-1]

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
            all_diff_commands_and_results_and_unmodified.append([commands,results[:-1],unmodified_1[:-1],unmodified_2[:-1]])
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
                if i[1]:
                    print(i[1])
                else:
                    return None

    def output_unmodified_from_original(self,diff):
        for i in self.get_all_diff_commands_and_results_and_unmodified():
            if diff.commands == i[0]:
                if i[2]:
                    print(i[2])
                else:
                    return None

    def output_unmodified_from_new(self,diff):
        for i in self.get_all_diff_commands_and_results_and_unmodified():
            if diff.commands == i[0]:
                if i[3]:
                    print(i[3])
                else:
                    return None

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
#     p = OriginalNewFiles('file_4_1.txt', 'file_4_2.txt')
#     diffs = p.get_all_diff_commands()
#     print(len(diffs))
#     print(diffs[0])
#     diff_1 = DiffCommands('diff_4.txt')
#     p.output_diff(diff_1)
#     p.output_unmodified_from_original(diff_1)









