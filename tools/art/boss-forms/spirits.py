"""Improve the approved curtain, residual armor and bound-head bodies in place."""
import sys
import presence as p
p.D=p.R/'docs/art/boss-presence-v5'
p.TARGETS=['eunuch_mastermind','rebel_general','xianzhen_duantoujiang']
p.SAMPLES={'eunuch_mastermind':[('idle',0),('idle',28),('attack',0),('attack',19)],
 'rebel_general':[('idle',0),('attack',9),('attack',12),('attack',22)],
 'xianzhen_duantoujiang':[('idle',0),('roar',18),('roar',24),('roar',44)]}
p.ATTACKS.update(eunuch_mastermind='attack',rebel_general='attack',xianzhen_duantoujiang='roar')
export=p.export
validate=p.validate
if __name__=='__main__':
 if '--review-only' not in sys.argv:export();validate()
 if '--export-only' not in sys.argv:p.review()
