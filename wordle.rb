require 'csv'
require 'minitest/autorun'

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
  NAMES = %w[L T F S].freeze
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

def load_data(file = File.expand_path('wordle.csv', __dir__))
  CSV.read(file, headers: true).map do |row|
    Game.new(row)
  end
end

games = load_data
scores = games.map(&:scores)
totals = Game::NAMES.map do |n|
  scn = scores.reduce(0) { |acc, s| acc + s.fetch(n, 0) }
  numbers = games.reject { |g| g.data[n].nil? }.size
  [n, scn, numbers, (scn / numbers.to_f).round(2)]
end
puts totals.map { |r| r.join(',') }.join("\n")

CSV.open('ranked.csv', 'w') do |csv|
  csv << Game::HEADERS
  games.each do |game|
    csv << game.to_csv
  end
end

class Test < Minitest::Test
  def test_avg_rank
    assert_equal({a: 1, b: 2}, avg_rank({a: 3, b: 4}))
    assert_equal({a: 2, b: 2, c: 2}, avg_rank({a: 1, b: 1, c: 1}))
    assert_equal({a: nil, b: 1}, avg_rank({a: nil, b: 6}))
    assert_equal({a: 1.5, b: 1.5, c: 3.5, d: 3.5}, avg_rank({a: 3, b: 3, c: 4, d: 4}))
  end
end
