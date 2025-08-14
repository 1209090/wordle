LASTN = 10

def average(array) = array.sum.to_f / array.size
def pretty_print(array, rev: true)
  sorted = array.sort_by(&:last)
  sorted.reverse! if rev
  sorted.map { _1.join(' ') }.join(', ')
end
stats = CSV.readlines 'stats.csv', headers: true
players = stats.headers[2..-1]
res = stats.reduce(Hash.new(0)) { |acc, row| players.each { |k| acc[k] += row[k].to_i }; acc }
puts pretty_print(res)
data = CSV.read('wordle.csv', headers: true)
res = data.headers[2..].map { |k| [k, average(data[k].first(LASTN).compact.map(&:to_i)).round(2)] }
puts pretty_print(res, rev: false)
coeff = res.map do |k, v|
  c =
    case
    when v <= 2 then 0.5
    when v >= 3 then 1.0
    else 0.5 + 0.5 * (v - 2)
    end
  [k, c]
end.to_h
corrected_res = players.map do |k|
  [k, (stats.first[k].to_f * coeff[k]).round]
end.to_h
puts pretty_print(corrected_res)
