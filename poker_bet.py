import pygame
import random

# カードのスートとランクを定義
suits = ['hearts', 'diamonds', 'clubs', 'spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

# カードクラス
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f'{self.rank}_of_{self.suit}'

# デッキクラス
class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

# プレイヤーのハンド
class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def replace_card(self, index, card):
        self.cards[index] = card

    def __repr__(self):
        return ', '.join(map(str, self.cards))

# 役を判定する関数
def evaluate_hand(hand):
    ranks_count = {rank: 0 for rank in ranks}
    suits_count = {suit: 0 for suit in suits}

    for card in hand.cards:
        ranks_count[card.rank] += 1
        suits_count[card.suit] += 1

    rank_counts = sorted(ranks_count.values(), reverse=True)
    flush = max(suits_count.values()) == 5
    straight = False
    rank_indices = [ranks.index(card.rank) for card in hand.cards]
    rank_indices.sort()
    
    if len(set(rank_indices)) == 5 and max(rank_indices) - min(rank_indices) == 4:
        straight = True

    if straight and flush:
        return "Straight Flush", 10
    elif rank_counts[0] == 4:
        return "Four of a Kind", 5
    elif rank_counts[0] == 3 and rank_counts[1] == 2:
        return "Full House", 4
    elif flush:
        return "Flush", 3
    elif straight:
        return "Straight", 2
    elif rank_counts[0] == 3:
        return "Three of a Kind", 1.5
    elif rank_counts[0] == 2 and rank_counts[1] == 2:
        return "Two Pair", 1.2
    elif rank_counts[0] == 2:
        return "One Pair", 1
    else:
        return "High Card", 0.5

# Pygameの初期化
pygame.init()

# 画面のサイズと設定
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Poker Game")

# カード画像のロード
def load_card_images():
    card_images = {}
    for suit in suits:
        for rank in ranks:
            filename = f'images/{rank}_of_{suit}.png'
            
            try:
                image = pygame.image.load(filename)
                key = f'{rank}_of_{suit}'
                card_images[key] = pygame.transform.scale(image, (100, 150))
              
            except pygame.error as e:
                print(f"Error loading image {filename}: {e}")
                
    return card_images

# カード画像の読み込み
card_images = load_card_images()

# ボタンの描画
def draw_button(text, rect, color, hover_color, font):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_x, mouse_y)
    pygame.draw.rect(screen, hover_color if is_hovered else color, rect, border_radius=15)
    pygame.draw.rect(screen, (0, 0, 0), rect, 3, border_radius=15)
    text_surface = font.render(text, True, (0, 0, 0))
    screen.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, 
                               rect.y + (rect.height - text_surface.get_height()) // 2))

# 入力ボックスの描画
def draw_input_box(rect, text, font, active, hover_color, default_color):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_x, mouse_y)
    pygame.draw.rect(screen, hover_color if is_hovered else default_color, rect, border_radius=15)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=15)
    text_surface = font.render(text, True, (0, 0, 0))
    screen.blit(text_surface, (rect.x + 10, rect.y + 10))
    if active:
        pygame.draw.rect(screen, (0, 0, 0), rect.inflate(4, 4), 1)  # 入力中のボックスに枠線

# カードの描画
def draw_hand(hand, x_start, y_start, selected_indices):
    x, y = x_start, y_start
    card_width, card_height = 100, 150
    card_spacing = 15
    overlay = pygame.Surface((card_width, card_height))  # カードサイズと同じ
    overlay.set_alpha(128)  # 半透明
    overlay.fill((255, 255, 255))  # 白いオーバーレイ

    card_rects = []
    for i, card in enumerate(hand.cards):
        card_key = str(card)
        card_rect = pygame.Rect(x, y, card_width, card_height)
        card_rects.append(card_rect)
        if card_key in card_images:
            if i in selected_indices:
                pygame.draw.rect(screen, (255, 0, 0), card_rect, 5)  # 選択されたカードに赤い枠線
            screen.blit(overlay, (x, y))  # カードの背後にオーバーレイを描画
            screen.blit(card_images[card_key], (x, y))  # カードを描画
        else:
            print(f"Image for {card_key} not found.")
        x += card_width + card_spacing  # カードの間隔

    return card_rects

def play_poker():
    num_games = 5
    initial_money = 1000  # 所持金の初期値
    current_money = initial_money
    current_game = 0
    bet = 0

    while True:
        if current_game < num_games:
            deck = Deck()
            player_hand = Hand()
            selected_indices = []  # 選択されたカードのインデックス
            exchange_done = False  # 交換が完了したかどうか

            # プレイヤーに5枚のカードを配る
            for _ in range(5):
                player_hand.add_card(deck.deal())

            # 交換ボタンの設定
            button_font = pygame.font.Font(None, 36)
            change_button_rect = pygame.Rect(50, 500, 200, 50)
            bet_button_rect = pygame.Rect(300, 500, 200, 50)
            change_button_text = 'Change'
            bet_button_text = 'Place Bet'

            # 掛け金入力ボックスの設定
            input_box = pygame.Rect(50, 400, 200, 50)
            font = pygame.font.Font(None, 32)
            input_text = ''
            input_active = False  # 初期状態では入力ボックスは非アクティブ

            # ボタンと入力ボックスのホバー時の色設定
            input_hover_color = (200, 255, 200)
            input_default_color = (255, 255, 255)
            button_hover_color = (150, 150, 255)
            button_default_color = (200, 200, 255)

            card_rects = draw_hand(player_hand, 50, 200, selected_indices)

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                    # マウスクリック処理
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos

                        # 入力ボックスのクリック処理
                        if input_box.collidepoint(x, y):
                            input_active = True
                        else:
                            input_active = False

                        # 交換ボタンのクリック処理
                        if change_button_rect.collidepoint(x, y) and not exchange_done and bet > 0:
                            for i in selected_indices:
                                new_card = deck.deal()
                                player_hand.replace_card(i, new_card)
                            selected_indices = []  # 選択解除
                            exchange_done = True  # 交換完了

                        # 掛け金ボタンのクリック処理
                        if bet_button_rect.collidepoint(x, y):
                            try:
                                bet = int(input_text)
                                if bet > current_money:
                                    bet = current_money
                                elif bet < 0:
                                    bet = 0
                                current_money -= bet
                            except ValueError:
                                bet = 0
                            input_text = ''  # 入力後にクリア
                            input_active = False
                            if bet > 0:
                                bet_button_rect = pygame.Rect(300, 500, 200, 50)  # ベットボタン位置再設定

                        # カードのクリック処理
                        for i, rect in enumerate(card_rects):
                            if rect.collidepoint(x, y):
                                if i in selected_indices:
                                    selected_indices.remove(i)
                                else:
                                    selected_indices.append(i)

                    # キーイベント処理
                    if input_active:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                try:
                                    bet = int(input_text)
                                    if bet > current_money:
                                        bet = current_money
                                    elif bet < 0:
                                        bet = 0
                                    current_money -= bet
                                except ValueError:
                                    bet = 0
                                input_text = ''  # 入力後にクリア
                                input_active = False
                            elif event.key == pygame.K_BACKSPACE:
                                input_text = input_text[:-1]
                            elif event.unicode.isalnum() or event.unicode in ' \b':
                                input_text += event.unicode

                # 画面のクリア
                screen.fill((200, 200, 200))  # 明るい灰色の背景

                # 手札の描画
                card_rects = draw_hand(player_hand, 50, 200, selected_indices)

                # 掛け金入力ボックスの描画
                draw_input_box(input_box, input_text, font, input_active, input_hover_color, input_default_color)

                # ボタンの描画
                draw_button(change_button_text, change_button_rect, 
                            button_default_color if bet > 0 else (200, 200, 200), 
                            button_hover_color, button_font)
                draw_button(bet_button_text, bet_button_rect, button_default_color, button_hover_color, button_font)

                # 役の判定結果を画面に表示
                hand_result, multiplier = evaluate_hand(player_hand)
                result_text = font.render(f'Hand: {hand_result}', True, (0, 0, 0))
                screen.blit(result_text, (50, 50))

                # 所持金と掛け金の表示
                money_text = font.render(f'Money: ${current_money}', True, (0, 0, 0))
                screen.blit(money_text, (50, 100))
                bet_text = font.render(f'Bet: ${bet}', True, (0, 0, 0))
                screen.blit(bet_text, (50, 150))

                pygame.display.flip()

                if exchange_done:
                    winnings = bet * multiplier
                    current_money += winnings
                    pygame.time.wait(3000)  # 3秒待機
                    current_game += 1
                    bet = 0  # 次のゲームのためにベットを初期化
                    break  # ゲームループから抜ける

            pygame.display.flip()

        else:
            # ゲーム終了時の処理
            screen.fill((255, 255, 255))  # 白い背景

            final_font = pygame.font.Font(None, 48)
            result_text = final_font.render(f'Final Money: ${current_money}', True, (0, 0, 0))
            screen.blit(result_text, (screen_width // 2 - result_text.get_width() // 2, screen_height // 2 - 50))

            # Retryボタンの設定
            retry_button_rect = pygame.Rect(screen_width // 2 - 70, screen_height // 2 + 20, 140, 50)
            retry_button_text = 'Retry'
            draw_button(retry_button_text, retry_button_rect, (255, 255, 255), (200, 200, 200), final_font)

            pygame.display.flip()

            retrying = True
            while retrying:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        if retry_button_rect.collidepoint(x, y):
                            # ゲームのリスタート
                            current_money = initial_money
                            current_game = 0
                            retrying = False  # ループから抜けてゲームを再スタート

if __name__ == '__main__':
    play_poker()
