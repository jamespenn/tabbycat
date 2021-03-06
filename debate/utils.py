from functools import wraps

def memoize(fn):
    cache = {}
    @wraps(fn)
    def foo(*args):
        if args not in cache:
            cache[args] = fn(*args)

        return cache[(args)]

    foo.func_name = fn.func_name
    return foo


def pair_list(ls):
    half = len(ls)/2
    return zip(ls[:half], ls[half:])

def gen_results():
    import random

    r = {'aff': (0,), 'neg': (0,)}

    def do():
        s = [random.randint(60, 80) for i in range(3)]
        s.append(random.randint(30,40))
        return s

    while sum(r['aff']) == sum(r['neg']):
        r['aff'] = do()
        r['neg'] = do()

    return r

def generate_random_results(round):
    # WARNING: This function has probably been broken by the transition to
    # using BallotSubmissions.  See data/utils/add_ballot_set.py for a new
    # example.
    from debate.models import Debate, DebateResult

    debates = Debate.objects.filter(round=round)

    for debate in debates:
        dr = DebateResult(debate)

        rr = gen_results()
        for side in ('aff', 'neg'):
            speakers = getattr(debate, '%s_team' % side).speakers
            scores = rr[side]
            for i in range(1, 4):
                dr.set_speaker(
                    side = side,
                    pos = i,
                    speaker = speakers[i - 1],
                )
            dr.set_speaker(
                side = side,
                pos = 4,
                speaker = speakers[0]
            )

            for adj in debate.adjudicators.list:
                for pos in range(1, 5):
                    dr.set_score(adj, side, pos, scores[pos-1])

        dr.save()
        debate.result_status = debate.STATUS_CONFIRMED
        debate.save()


def test_gen():
    from debate.models import Round
    generate_random_results(Round.objects.get(pk=1))

def make_dummy_speakers():
    from debate import models as m
    t = m.Tournament.objects.get(pk=1)

    for team in t.teams:
        assert m.Speaker.objects.filter(team=team).count() == 0
        for i in range(1, 4):
            m.Speaker(name='%s %d' % (team, i), team=team).save()


