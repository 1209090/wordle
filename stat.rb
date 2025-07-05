LASTN = 10

def average(array) = array.sum.to_f / array.size 
def pretty_print(array, rev: true)
  sorted = array.sort_by(&:last)
  sorted.reverse! if rev
  sorted.map { _1.join(' ') }.join(', ')
end
data = CSV.readlines 'stats.csv', headers: true 
players = data.headers[2..-1] 
res = data.reduce(Hash.new(0)) { |acc, row| players.each { |k| acc[k] += row[k].to_i }; acc } 
puts pretty_print(res) 
data = CSV.read('wordle.csv', headers: true) 
res = data.headers[2..].map { |k| [k, average(data[k].first(LASTN).compact.map(&:to_i)).round(2)] } 
puts pretty_print(res, rev: false)

