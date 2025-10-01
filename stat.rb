LASTN = 10

def average(array)
  return 0 if array.empty?
  array.sum.to_f / array.size
end

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
  real = stats.first[k].to_i
  corrected = (real * coeff[k]).round
  val = corrected.to_s
  val += " (#{real})" if real != corrected
  [k, val]
end.to_h
puts pretty_print(corrected_res)

year = data.select { |row| row['id'].to_i >= 1257 }
ys = year.reduce({}) do |acc, row|
  players.each do |k|
    acc[k] ||= []
    acc[k] << row[k].to_i if row[k]
  end
  acc
end
pp ys.transform_values { avg = average(_1).round(3); _1.tally.sort_by(&:first).to_h.merge('avg' => avg) }
