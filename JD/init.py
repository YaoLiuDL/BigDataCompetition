__author__ = 'ly'
from gen_feat import make_train_set
from gen_feat import make_test_set
from sklearn.model_selection import train_test_split
import xgboost as xgb
from gen_feat import report

import numpy as np

train_start_date = '2016-03-06'
train_end_date = '2016-04-06'
test_start_date = '2016-04-06'
test_end_date = '2016-04-11'

sub_start_date = '2016-03-11'
sub_end_date = '2016-04-11'
sub_test_start_date = '2016-04-11'
sub_test_end_date = '2016-04-16'

user_index, training_data, label = make_train_set(train_start_date, train_end_date, test_start_date, test_end_date)
X_train, X_test, y_train, y_test = train_test_split(training_data, label, test_size=0.2, random_state=0)
del user_index, training_data, label
dtrain=xgb.DMatrix(X_train.values, label=y_train) #todo: missing=-999.0
dtest=xgb.DMatrix(X_test.values, label=y_test)
del X_train, X_test, y_train, y_test
# param = {'max_depth': 10, 'eta': 0.05, 'silent': 1, 'objective': 'binary:logistic'}
param = {'learning_rate' : 0.1, 'n_estimators': 1000, 'max_depth': 3, 
    'min_child_weight': 5, 'gamma': 0, 'subsample': 1.0, 'colsample_bytree': 0.8,
    'scale_pos_weight': 1, 'eta': 0.05, 'silent': 1, 'objective': 'binary:logistic'}
num_round = 4000
param['nthread'] = 6
param['eval_metric'] = "auc"
plst = param.items()
plst += [('eval_metric', 'logloss')]
evallist = [(dtest, 'eval'), (dtrain, 'train')]
bst=xgb.train( plst, dtrain, num_round, evallist)
del dtrain	
print('saving model...')
# flag = 'basic'
# bst.save_model('./cache/' + flag + '_model')
sub_user_index, sub_training_data, sub_label = make_train_set(sub_start_date, sub_end_date,
                                                               sub_test_start_date, sub_test_end_date, test=True)
test = xgb.DMatrix(sub_training_data.values)
y = bst.predict(test)

pred = sub_user_index.copy()
pred['label'] = y
pred = pred.sort_values(by=['label'], ascending=False).groupby(['user_id'], as_index=False).first()

limits = np.linspace(0, 0.5, 100)
scores = np.zeros((1,100))
count = 0
for i in limits:
	print('--------------------------------------------------------------------')
	print('limit=%s' % str(i))
	p = pred[pred['label'] > i]
	scores[:, count] = report(p, sub_label)
	count += 1

print('max score : %s\nmax limit : %s' % (np.max(scores), limits[np.argmax(scores)]))