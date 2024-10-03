# /usr/bin/env ruby wordle.rb
python3 wordle.py
/usr/bin/env ruby -rcsv \
  -e "data = CSV.readlines 'week-champs.csv', headers: true" \
  -e "players = data.headers[2..-1]" \
  -e "res = data.reduce(Hash.new(0)) { |acc, row| players.each { |k| acc[k] += row[k].to_i }; acc }" \
  -e "puts res.sort_by(&:last).reverse.map { _1.join(' ') }.join(', ')"
