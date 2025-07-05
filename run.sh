python3 wordle.py
/usr/bin/env ruby -rcsv stat.rb
#   -e "def average(array) = array.sum.to_f / array.size" \
#   -e "def pretty_print(array, rev: true) = array.sort_by(&:last).reverse.map { _1.join(' ') }.join(', ')" \
#   -e "data = CSV.readlines 'stats.csv', headers: true" \
#   -e "players = data.headers[2..-1]" \
#   -e "res = data.reduce(Hash.new(0)) { |acc, row| players.each { |k| acc[k] += row[k].to_i }; acc }" \
#   -e "puts pretty_print(res)" \
#   -e "data = CSV.read('wordle.csv', headers: true)" \
#   -e "res = data.headers[2..].map { |k| [k, average(data[k][0..20].compact.map(&:to_i)).round(2)] }" \
#   -e "puts pretty_print(res)"
