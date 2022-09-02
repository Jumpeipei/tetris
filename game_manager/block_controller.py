#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import copy

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):
        
        t1 = datetime.now()

        # print GameStatus
        print("=================================================>")
        pprint.pprint(GameStatus, width = 61, compact = True)

        # get data from GameStatus
        # current shape info
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        self.CurrentShape_index = GameStatus["block_info"]["currentShape"]["index"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]

        # search best nextMove -->
        strategy = None
        LatestEvalValue = -100000
        iter = 0
        # search with current block Shape
        for direction0 in CurrentShapeDirectionRange:
            # search with x range
            x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
            for x0 in range(x0Min, x0Max):
                # get board data, as if dropdown block
                board, dy = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)
                #print(self.getShapeCoordArray(self.CurrentShape_class, direction0, x0, 0))

                # evaluate board
                EvalValue = self.calcEvaluationValueSample(board, direction0, x0, dy)
                # update best move
                if EvalValue > LatestEvalValue:
                    strategy = (direction0, x0, 1, 1)
                    LatestEvalValue = EvalValue

                ###test
                ###for direction1 in NextShapeDirectionRange:
                ###  x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                ###  for x1 in range(x1Min, x1Max):
                ###        board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                ###        EvalValue = self.calcEvaluationValueSample(board2)
                ###        if EvalValue > LatestEvalValue:
                ###            strategy = (direction0, x0, 1, 1)
                ###            LatestEvalValue = EvalValue
                iter += 1
        # search best nextMove <--

        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        print([strategy[1], strategy[2]])
        print("###### Jumpei CODE ######")
        return nextMove

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        current_mino_index = self.CurrentShape_index
        i_mino_index = 1
        if current_mino_index == 1 or current_mino_index == 2 or current_mino_index == 5:
            return xMin, xMax
        else:
            return xMin, xMax - 1
    
    def empty_enough_line(self, board, min_height):
        bottom = self.board_data_height - 1
        for y in range(self.board_data_height - 1, 0, -1):
            if board[y * self.board_data_width + (self.board_data_width - 1)] != self.ShapeNone_index:
                bottom = y
        
        if (bottom - min_height) < 3:
            return False
    
    def i_mino(self, board, x, y, direction):
        hole_blocks = 0
        if direction == 0:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1
            
            x_3 = x
            y_3 = y + 1
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1

            x_4 = x
            y_4 = y + 2
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 1:
            x_1 = x - 2
            y_1 = y
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x - 1
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1
            
            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1

            x_4 = x + 1
            y_4 = y
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        return hole_blocks
    
    def l_mino(self, board, x, y, direction):
        hole_blocks = 0
        if direction == 0:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y + 1
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x + 1
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 1:
            x_1 = x - 1
            y_1 = y
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x + 1
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x - 1
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1
        elif direction == 2:
            x_1 = x - 1
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y - 1
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 3:
            x_1 = x + 1
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x - 1
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x + 1
            y_4 = y
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        return hole_blocks

    def j_mino(self, board, x, y, direction):
        hole_blocks = 0
        if direction == 0:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y + 1
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x - 1
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 1:
            x_1 = x - 1
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x - 1
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x + 1
            y_4 = y
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1
        elif direction == 2:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x + 1
            y_2 = y - 1
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 3:
            x_1 = x - 1
            y_1 = y
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x + 1
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x + 1
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        return hole_blocks

    def t_mino(self, board, x, y, direction):
        hole_blocks = 0
        if direction == 0:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x + 1
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 1:
            x_1 = x
            y_1 = y + 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x - 1
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x + 1
            y_4 = y
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1
        elif direction == 2:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x - 1
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 3:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x - 1
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x + 1
            y_4 = y
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        return hole_blocks
    
    def o_mino(self, board, x, y, direction):
        hole_blocks = 0
        if direction == 0:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x + 1
            y_2 = y - 1
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1

            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1
            
            x_4 = x + 1
            y_4 = y
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1
        
        return hole_blocks

    def s_mino(self, board, x, y, direction):
        hole_blocks = 0
        if direction == 0:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x + 1
            y_2 = y - 1
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1
            
            x_3 = x - 1
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1

            x_4 = x
            y_4 = y
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 1:
            x_1 = x
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1
            
            x_3 = x + 1
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1

            x_4 = x + 1
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        return hole_blocks

    def z_mino(self, board, x, y, direction):
        hole_blocks = 0
        if direction == 0:
            x_1 = x - 1
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y - 1
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1
            
            x_3 = x
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1

            x_4 = x + 1
            y_4 = y
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 + below_4) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        elif direction == 1:
            x_1 = x + 1
            y_1 = y - 1
            below_1 = 1
            while (y_1 + below_1) <= (self.board_data_height - 1) and board[(y_1 + below_1) * self.board_data_width + x_1] == self.ShapeNone_index:
                hole_blocks += 1
                below_1 += 1
            
            x_2 = x
            y_2 = y
            below_2 = 1
            while (y_2 + below_2) <= (self.board_data_height - 1) and board[(y_2 + below_2) * self.board_data_width + x_2] == self.ShapeNone_index:
                hole_blocks += 1
                below_2 += 1
            
            x_3 = x + 1
            y_3 = y
            below_3 = 1
            while (y_3 + below_3) <= (self.board_data_height - 1) and board[(y_3 + below_3) * self.board_data_width + x_3] == self.ShapeNone_index:
                hole_blocks += 1
                below_3 += 1

            x_4 = x
            y_4 = y + 1
            below_4 = 1
            while (y_4 + below_4) <= (self.board_data_height - 1) and board[(y_4 - 1) * self.board_data_width + x_4] == self.ShapeNone_index:
                hole_blocks += 1
                below_4 += 1

        return hole_blocks

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board, dy = self.dropDown(board, Shape_class, direction, x)
        return _board, dy

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board, dy

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        return _board

    def calcEvaluationValueSample(self, board, direction, x_center, y_center):
        #
        # sample function of evaluate board.
        #
        width = self.board_data_width
        height = self.board_data_height

        # evaluation paramters
        ## lines to be removed
        fullLines = 0
        ## number of holes or blocks in the line.
        nHoles, nIsolatedBlocks = 0, 0
        ## absolute differencial value of MaxY
        absDy = 0
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width
        adjacent_blocks = 0
        hole_blocks = 0
        penalty = 0
        ### check board
        # each y linee
        for y in range(height - 1, 0, -1):
            hasHole = False
            hasBlock = False
            # each x line
            for x in range(width):
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index:
                    # hole
                    hasHole = True
                    holeCandidates[x] += 1  # just candidates in each column..
                else:
                    # block
                    hasBlock = True
                    BlockMaxY[x] = height - y                # update blockMaxY
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]  # update number of holes in target column..
                        holeCandidates[x] = 0                # reset
                    if holeConfirm[x] > 0:
                        nIsolatedBlocks += 1                 # update number of isolated blocks

            if hasBlock == True and hasHole == False:
                # filled with block
                
                fullLines += 1
            elif hasBlock == True and hasHole == True:
                # do nothing
                pass
            elif hasBlock == False:
                # no block line (and of course no hole)
                pass

        if self.CurrentShape_index == 1:
            hole_blocks += self.i_mino(board, x_center, y_center, direction)
            if direction == 0:
                enough_lines = self.empty_enough_line(board, min(BlockMaxY))
                if not enough_lines == True:
                    penalty += 2.0
        if self.CurrentShape_index == 2:
            hole_blocks += self.l_mino(board, x_center, y_center, direction)
        if self.CurrentShape_index == 3:
            hole_blocks += self.j_mino(board, x_center, y_center, direction)
        if self.CurrentShape_index == 4:
            hole_blocks += self.t_mino(board, x_center, y_center, direction)
        if self.CurrentShape_index == 5:
            hole_blocks += self.o_mino(board, x_center, y_center, direction)
        if self.CurrentShape_index == 6:
            hole_blocks += self.s_mino(board, x_center, y_center, direction)
        if self.CurrentShape_index == 7:
            hole_blocks += self.z_mino(board, x_center, y_center, direction)

        # nHoles
        for x in holeConfirm:
            nHoles += abs(x)

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(len(BlockMaxY) - 1):
            val = BlockMaxY[i] - BlockMaxY[i+1]
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)

        #### maxDy
        #maxDy = max(BlockMaxY) - min(BlockMaxY)
        #### maxHeight
        #maxHeight = max(BlockMaxY) - fullLines

        ## statistical data
        #### stdY
        #if len(BlockMaxY) <= 0:
        #    stdY = 0
        #else:
        #    stdY = math.sqrt(sum([y ** 2 for y in BlockMaxY]) / len(BlockMaxY) - (sum(BlockMaxY) / len(BlockMaxY)) ** 2)
        #### stdDY
        #if len(BlockMaxDy) <= 0:
        #    stdDY = 0
        #else:
        #    stdDY = math.sqrt(sum([y ** 2 for y in BlockMaxDy]) / len(BlockMaxDy) - (sum(BlockMaxDy) / len(BlockMaxDy)) ** 2)

        # calc Evaluation Value
        score = 0
        if fullLines == 4:
            score = score + fullLines * 10.0
        elif fullLines == 3:
            score = score + fullLines * 0.5
        elif fullLines == 2:
            score = score + fullLines * 0.5
        else:
            score = score + fullLines * 0.5         # try to delete line 
        score = score - nHoles * 5.0               # try not to make hole
        score = score - nIsolatedBlocks * 2.0      # try not to make isolated block
        score = score - absDy * 1.0                # try to put block smoothly
        score = score - hole_blocks * 5.0
        score = score - penalty
        #score = score - maxDy * 0.3                # maxDy
        #score = score - maxHeight * 5              # maxHeight
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.01               # statistical data
        # print(score, fullLines, nHoles, nIsolatedBlocks, maxHeight, stdY, stdDY, absDy, BlockMaxY)
        return score

BLOCK_CONTROLLER = Block_Controller()

