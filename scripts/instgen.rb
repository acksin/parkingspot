require 'json'

j = JSON.parse(open(ARGV[0]).read)
puts "package stats"
print "var instanceTypeCsv = `"

j['config']['regions'].each do |i|
  it = i['instanceTypes'].map { |x| x['sizes'] }.flatten

  it.each do |inst|
    puts [i['region'], inst['size'], inst['vCPU'], inst['ECU'], inst['memoryGiB'], inst['valueColumns'][0].select { |x| x == 'prices' }['prices']['USD']].join(',')
  end
end

puts "`"
