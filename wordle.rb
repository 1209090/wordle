require 'csv'
require 'elo_rating'
# require 'minitest/autorun'

def avg_rank(values)
  nils = values.select { |k, v| v.nil? }
  ranked = values.compact.reduce(Hash.new { |h, k| h[k] = [] }) do |acc, (k, v)|
    acc[v] << k
    acc
  end.to_a.sort_by(&:first)
  res = {}
  idx = 1
  ranked.each do |_, keys|
    rank = keys.reduce(0) do |acc, _|
      acc += idx
      idx += 1
      acc
    end
    rank = rank.to_f / keys.size
    keys.each do |k|
      res[k] = rank
    end
  end
  res.merge(nils)
end

class Game
  NAMES = %w[L T F S R B].freeze
  HEADERS = (%w[id word] + NAMES + NAMES.map { |n| "#{n} rank" }).freeze

  attr_reader :word, :id, :data

  def initialize(row)
    @data = {}
    @word = row['word']
    @id = row['id'].to_i
    NAMES.each do |n|
      @data[n] = row[n].to_i if row[n]
    end
  end

  def inspect
    res = NAMES.map { |n| data[n] ? "#{n}: #{data[n]}" : nil }.compact.join(', ')
    "(#{id}, #{word}, #{res}, #{scores})"
  end

  def scores(rank = 2, guesses = 1)
    number = data.compact.size
    ranks.reduce({}) { |acc, (k, v)| acc[k] = ((number - v) * rank + (6 - data[k]) * guesses); acc }
  end

  def ranks
    @ranks ||= avg_rank(data)
  end

  def to_csv
    [id, word, *NAMES.map { |n| data[n] }, *NAMES.map { |n| ranks[n] }]
  end
end

class Scores
  attr_reader :games

  def initialize(games)
    @games = games
  end

  def average_rank
    games.reduce({}) do |acc, game|
      next acc if game.ranks.compact.size == 1
      game.ranks.each do |name, rank|
        acc[name] ||= []
        acc[name] << rank
      end
      acc
    end.transform_values { |ranks| ranks.sum / ranks.size }
  end

  def metric1
    games.reduce(Hash.new { |h, k| h[k] = [] }) do |acc, game|
      vals = game.data.values.compact
      avg = vals.sum.to_f / vals.size
      game.data.each do |name, num|
        next if num.nil?
        acc[name] << avg - num
      end
      acc
    end.transform_values { |scs| scs.sum }
  end

  def last_metric1(number = nil)
    number ||= games.size
    games.last(number).each_with_index.reverse_each.reduce({}) do |acc, (game, idx)|
      vals = game.data.values.compact
      avg = vals.sum.to_f / vals.size
      Game::NAMES.each do |name|
        num = game.data.fetch(name, nil)
        acc[name] ||= []
        acc[name] << (num ? avg - num : 0)
      end
      acc
    end
  end
end

def load_data(file = File.expand_path('wordle.csv', __dir__))
  CSV.read(file, headers: true).map do |row|
    Game.new(row)
  end.reverse
end

def puts_scores(title, data)
  puts title
  puts data.to_a.sort_by(&:last).map { |a| "#{a[0]}\t#{a[1].round(3)}" }.join("\n")
end

# Copied from ActiveSupport
def in_groups(arr, number, &block)
  division = arr.size.div(number)
  modulo = arr.size % number

  groups = []
  start = 0

  number.times do |index|
    length = division + (modulo > 0 && modulo > index ? 1 : 0)
    groups << arr.slice(start, length)
    start += length
  end

  if block_given?
    groups.each(&block)
  else
    groups
  end
end

games = load_data
scores = Scores.new(games)

def elo(games)
  init_rating = 1000
  players = [Game::NAMES.each_with_object({}) { |name, acc| acc[name] = init_rating }]
  games.each do |game|
    match = EloRating::Match.new
    places = game.ranks.compact.to_a
    places.each do |name, place|
      match.add_player(rating: players.last[name], place: place)
    end
    new_rating = Game::NAMES.each_with_object({}) do |name, acc|
      idx = places.index { |n, _| n == name }
      acc[name] =
        if idx
          match.updated_ratings[idx]
        else
          players.last[name]
        end
    end
    new_rating['word'] = game.word
    players << new_rating
  end
  players
end

minmax = [2000, 0]
CSV.open('elo.csv', 'w') do |csv|
  csv << ['слово'] + Game::NAMES
  ratings = elo(games)
  header = ratings.shift
  ratings.reverse_each do |data|
    row = Game::NAMES.map { |n| data[n] }
    row.each do |rating|
      minmax[0] = rating if minmax[0] > rating
      minmax[1] = rating if minmax[1] < rating
    end
    row.unshift(data['word'])
    csv << row
  end
end
p minmax

# puts_scores('Average rank', scores.average_rank)
# puts_scores('Metric1', scores.last_metric1(4 * 7))

num = 4
output = [' ' * 11 + games.last(num * 7).reverse.map(&:word).join(' ')]

absolute = games.reduce(Hash.new(0)) do |acc, game|
  if game.ranks.compact.size > 1
    name, _ = game.ranks.find { |_, v| v == 1 }
    acc[name] += 1 if name
  end
  acc
end

puts absolute.sort_by(&:last).reverse.map { |n, sc| '%s% 3i' % [n, sc] }.join(', ')

__END__
scores = games.map(&:scores)
totals = Game::NAMES.map do |n|
  scn = scores.reduce(0) { |acc, s| acc + s.fetch(n, 0) }
  numbers = games.reject { |g| g.data[n].nil? }.size
  [n, scn, numbers, (scn / numbers.to_f).round(2)]
end
puts totals.map { |r| r.join(',') }.join("\n")

class Test < Minitest::Test
  def test_avg_rank
    assert_equal({a: 1, b: 2}, avg_rank({a: 3, b: 4}))
    assert_equal({a: 2, b: 2, c: 2}, avg_rank({a: 1, b: 1, c: 1}))
    assert_equal({a: nil, b: 1}, avg_rank({a: nil, b: 6}))
    assert_equal({a: 1.5, b: 1.5, c: 3.5, d: 3.5}, avg_rank({a: 3, b: 3, c: 4, d: 4}))
  end
end
