# Train
./ftrl_train -f agaricus.txt.train -m model_file

echo "-------------TSET------------"

# Test
./ftrl_predict -t agaricus.txt.test -m model_file -o pred.txt

