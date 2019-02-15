import chess
import numpy as np

def get_tables():
    states = {}
    moves = {}
    order = ['P','N','B','R','Q','K','p','n','b','r','q','k']
    for el in order:
        states[el] = np.zeros([8,8],int)
        moves[el] = np.zeros([8,8],int)
    return states, moves

def parse_board(board): # 
    '''return board of figures with position in form 
    of dict of pieces with assigned positions'''
    p_dict = board.piece_map()
    d_by_piece = {}
    for i in p_dict:
        pie = p_dict[i].symbol()
        x = chess.square_file(i)
        y = chess.square_rank(i)
        s = (x, y)
        if pie not in d_by_piece:
            d_by_piece[pie] = [s,]
        else:
            d_by_piece[pie].append(s)

    return d_by_piece

def parse_lan(lan, board): # REWRITE IN CASE OF PROMOTION !!!!
    is_white = board.turn
    d = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
    pieces_values = {'P':1,'N':2,'B':2,'R':3,'Q':4,'K':5,'p':1,'n':2,'b':2,'r':3,'q':4,'k':5}
    if 'x' in lan:
        strt, fin = lan.split('x')
    else:
        strt, fin = lan.split('-')
    if len(strt)>2:
        fig = (strt[0].upper() if is_white else strt[0].lower())
        a = (7-d[strt[1]],7-(int(strt[2])-1))
    else:
        fig = ('P' if is_white else 'p')
        a = (7-d[strt[0]],7-(int(strt[1])-1))
    if '=' in fin:
        mv, fg = fin.split('=')
        fg = fg[0]
        fig_promoted = (fg.upper() if is_white else fg.lower())
        b = (7-d[mv[0]],7-(int(mv[1])-1))
    else:
        fig_promoted = None
        b = (7-d[fin[0]],7-(int(fin[1])-1))
    if 'x' in lan:
        taken_fig_name = board.piece_at(chess.square(b[0],b[1]))
        taken_fig = pieces_values[taken_fig_name]
    else:
        taken_fig = 0
    return fig, a, b, fig_promoted, taken_fig

def calc_step(board):
    epoch_rate = 1
    dct_of_states_and_legal_moves = {}
    m = board.generate_legal_moves()
    reward = 0
    for j in m:
        move = chess.Move.from_uci(str(j))
        lan = board.lan(move)
        fig, a, b, fig_prom, taken_fig = parse_lan(lan,board)
        if fig not in dct_of_states_and_legal_moves:
            dct_of_states_and_legal_moves[fig] = {}
        if a not in dct_of_states_and_legal_moves[fig]:
            dct_of_states_and_legal_moves[fig][a] = {}
        reward_in_b = taken_fig
        if b not in dct_of_states_and_legal_moves[fig][a]:
            dct_of_states_and_legal_moves[fig][a][b] = [{},reward_in_b]
        board.push(move)
        #number = len(list(board.generate_legal_moves()))
        over = board.is_game_over()
        if not over:#number != 0: 
            m1 = board.generate_legal_moves()
            for k in m1:
                move1 = chess.Move.from_uci(str(k))
                lan1 = board.lan(move1)
                fig1, a1, b1, fig_prom1, taken_fig1 = parse_lan(lan1,board)
                if fig1 not in dct_of_states_and_legal_moves[fig][a][b][0]:
                    dct_of_states_and_legal_moves[fig][a][b][0][fig1] = {}
                if a1 not in dct_of_states_and_legal_moves[fig][a][b][0][fig1]:
                    dct_of_states_and_legal_moves[fig][a][b][0][fig1][a1] = []
                dct_of_states_and_legal_moves[fig][a][b][0][fig1][a1].append(b1)
                board.push(move1)
                over1 = board.is_game_over()
                if over1:
                    res = board.result()
                    scr = res.split('-')[0]
                    scr = 0.5 if '/' in scr else int(scr)
                    reward = - 10**epoch_rate * (2*(scr-0.5))
                    dct_of_states_and_legal_moves[fig][a][b][0][fig1][a1] = [{}, reward + reward_in_b]
                else:
                    # add here
                    pass
                board.pop()
        else: 
            res = board.result()
            scr = res.split('-')[0]
            scr = 0.5 if '/' in scr else int(scr)
            reward = 10**epoch_rate * (2*(scr-0.5))
            dct_of_states_and_legal_moves[fig][a][b] = [{}, reward + reward_in_b]
        board.pop()

    return board, dct_of_states_and_legal_moves
        # print(board)

board = chess.Board()
board, dct_of_states_and_legal_moves = calc_step(board)
figures_pos_dict = parse_board(board)
states, moves = get_tables()
state_order = ['P','N','B','R','Q','K','p','n','b','r','q','k']
moves_order = ['P','N','B','R','Q','K','p','n','b','r','q','k']
for my_fgr in dct_of_states_and_legal_moves:
    if my_fgr in states:
        for x,y in dct_of_states_and_legal_moves[my_fgr]:
            states[my_fgr][y,x] = 1
# print(states)
# print(dct_of_states_and_legal_moves)



# USEFUL EXAMPLE
# board.clear()
# print(board)
# board.set_piece_at(chess.square(0,6),chess.Piece.from_symbol('P'))
# board.set_piece_at(chess.square(1,7),chess.Piece.from_symbol('q'))
# board.set_piece_at(chess.square(3,7),chess.Piece.from_symbol('k'))
# print(board)
# mvs = board.generate_legal_moves()
# for i in mvs:
#     move1 = chess.Move.from_uci(str(i))
#     lan1 = board.lan(move1)
#     print(str(lan1))
# print(board.piece_at(chess.square(3,7)))
