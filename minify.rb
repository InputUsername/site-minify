require 'fileutils'

# Make or empty output dir
unless File.directory?('out') then
  puts('Creating \'out/\'')
	
	FileUtils.mkdir_p('out')
end

puts('Cleaning \'out/\'')

FileUtils.rm_rf(Dir.glob('out/*'))

# Minify style
puts('Minifying CSS')

require 'net/http'

style_files = Dir.glob('*.css')

uri = URI('http://cssminifier.com/raw')

style_files.each do |file|
	file_content = File.read(file)
	res = Net::HTTP.post_form(uri, 'input' => file_content)
	File.write('out/' + file, res.body)
end

# Minify pages
puts('Minifying pages')

page_files = Dir.glob('*.{html,php}')

def linked_style(file)
	"<link rel=\"stylesheet\" href=\"#{file}\" type=\"text/css\">"
end
def embed_style(file)
	"<style type=\"text/css\">\n#{File.read(file)}\n</style>"
end

page_files.each do |file|
    puts('* ' + file)
    
	# Remove tabs, carriage returns and extra newlines
	file_content = File.read(file)
		.gsub(/[\t\r]/, '')
		.gsub(/\n{2,}/, "\n")

	# Embed styles
	style_files.each do |style_file|
		file_content.gsub!(
			linked_style(style_file),
			embed_style('out/' + style_file)
		)
	end


	File.write('out/' + file, file_content)
end

# Remove s.css
FileUtils.rm_rf('out/s.css')

# Copy other files
puts('Copying other files')

other_files = %w(i.png space320.png)

other_files.each do |file|
    puts('* ' + file)
    
	FileUtils.copy_entry(file, 'out/' + file)
end

puts('Done')
