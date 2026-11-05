from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'mathing_pennies2'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    COOPERATE = 'cooperate'
    SAFE = 'safe'

    AI_ADVICE_TEXT = (
        'AIは「協力する」を推奨します。'
        'ただし、相手が安全策を選ぶ場合には、'
        'あなたの得点は0点になるリスクがあります。'
    )

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # 1ラウンド目だけ入力
    full_name = models.StringField(
        label='学籍番号',
        blank=False,
        max_length=100
    )

    # 各ラウンドで入力する「相手が協力すると思う確率」
    belief = models.IntegerField(
        min=0,
        max=100,
        label='相手が協力する確率は何％だと思いますか？'
    )

    decision = models.StringField(
        choices=[
            [C.COOPERATE, '協力する'],
            [C.SAFE, '安全策を選ぶ'],
        ],
        widget=widgets.RadioSelect,
        label='あなたはどちらを選びますか？'
    )

    # 最後のアンケート（round 3のみ回答）
    ai_trust = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
        label='AIの助言をどの程度信頼しましたか？（1=まったく信頼しなかった、7=非常に信頼した）',
        blank=True
    )

    decision_reason = models.LongStringField(
        label='3回のゲーム全体を通して、あなたがそのような選択をした主な理由を教えてください。',
        blank=True
    )

    free_comment = models.LongStringField(
        label='実験について気づいたことや感じたことがあれば自由に書いてください。（任意）',
        blank=True
    )


def creating_session(subsession: Subsession):
    # 各ラウンドでランダムにマッチング
    subsession.group_randomly(fixed_id_in_group=False)


class NameInput(Page):
    form_model = 'player'
    form_fields = ['full_name']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # 2ラウンド目以降でも参照できるよう participant に保存
        player.participant.full_name = player.full_name


class Rules(Page):
    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number == 1:
            condition_text = '　　　'
        elif player.round_number == 2:
            condition_text = '今回はAIから助言が提示されます。相手にもAIの助言が提示されているかどうかは分かりません。'
        else:
            condition_text = '今回はAIから助言が提示されます。さらに、相手にも同じAIの助言が提示されていることが分かっています。'

        return dict(
            condition_text=condition_text,
            ai_advice_text=C.AI_ADVICE_TEXT
        )


class Decision(Page):
    form_model = 'player'
    form_fields = ['belief','decision']

    @staticmethod
    def vars_for_template(player: Player):
        show_advice = player.round_number in [2, 3]

        if player.round_number == 1:
            round_label = '第1ゲーム'
            condition_explanation = '　　　'
        elif player.round_number == 2:
            round_label = '第2ゲーム'
            condition_explanation = '相手がAIの助言を受けているかどうかは分かりません。'
        else:
            round_label = '第3ゲーム'
            condition_explanation = '相手もあなたと同じAIの助言を受けていることが分かっています。'

        return dict(
            show_advice=show_advice,
            advice=C.AI_ADVICE_TEXT,
            round_label=round_label,
            condition_explanation=condition_explanation
        )


class PairWait(WaitPage):
    body_text = '相手の回答を待っています。結果は表示されません。'

    @staticmethod
    def after_all_players_arrive(group: Group):
        p1, p2 = group.get_players()

        if p1.decision == 'cooperate' and p2.decision == 'cooperate':
            p1.payoff = 10
            p2.payoff = 10
        elif p1.decision == 'safe' and p2.decision == 'safe':
            p1.payoff = 6
            p2.payoff = 6
        elif p1.decision == 'cooperate' and p2.decision == 'safe':
            p1.payoff = 0
            p2.payoff = 6
        else:
            p1.payoff = 6
            p2.payoff = 0


class FinalSurvey(Page):
    form_model = 'player'
    form_fields = ['ai_trust', 'decision_reason', 'free_comment']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        p1 = player.in_round(1)
        p2 = player.in_round(2)
        p3 = player.in_round(3)

        return dict(
            belief_r1=p1.belief,
            belief_r2=p2.belief,
            belief_r3=p3.belief,
            choice_r1=p1.decision,
            choice_r2=p2.decision,
            choice_r3=p3.decision,
        )


class Finish(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    NameInput,
    Rules,
    Decision,
    PairWait,
    FinalSurvey,
    Finish
]
