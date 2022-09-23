"""Site content management toolset thingy~"""
import clicore # https://github.com/AnotherTwinkle/clicore
import requests
import os
import time
import urllib

class WritingUtils(clicore.Module):
	def convert_to_styled_html(self, md, name = None):
		url = 'https://dillinger.io/factory/fetch_html'
		payload = {
			"name" : name or "Article",
			"unmd" : md,
			"formatting" : True,
			"preview" : False
		}

		response = requests.post(url, payload)
		assert response.status_code == 200

		return response.text

	def parse_latex_in_md(self, md):
		while True:
			start = md.find('$')
			end = md.find('$', start + 1)
			if -1 in [start, end]:
				break
			latex = md[start:end+1]
			link = f'![{latex[1:-1]}](https://latex.codecogs.com/svg.image?{urllib.parse.quote(latex[1:-1])})'
			md = md.replace(latex, link)

		return md

	@clicore.command(name = 'md')
	def md(self, ctx):
		pass	

	@clicore.add_flag(name = 'output', default = f'lab/produce/out{int(time.time())}.html')
	@md.command(name = 'parse')
	def parse_md(self, ctx, md_path):
		with open(md_path, 'r', encoding= 'utf-8') as file:
			md = file.read()

		md = self.parse_latex_in_md(md)
		html = self.convert_to_styled_html(md)
		if not os.path.exists('lab/produce'): os.makedirs('lab/produce');

		with open(ctx.flags.output , 'w', encoding= 'utf-8') as file:
			file.write(html)

	@clicore.add_flag(name = 'filename', default = 'writing.html')
	@clicore.add_flag(name = 'date', default = None)
	@clicore.add_flag(name = 'title', default = 'Untitled')
	@md.command(name='publish')
	def publish_md(self, ctx, md_path):
		"""Automatically handle all the indexing stuff, and publish a markdown as html"""
		with open(md_path, 'r', encoding= 'utf-8') as file:
			md = file.read()

		filename = ctx.flags.filename
		date = ctx.flags.date
		title = ctx.flags.title

		text= self.parse_latex_in_md(md)
		text = self.convert_to_styled_html(md)

		curdir = __file__.split(os.path.sep)[:-1]
		directory = date.split('/')[::-1] if date else 'undated'
		path = os.path.join('writings', *directory) if date else os.path.join('writings', 'undated')

		if not os.path.exists(path):
			os.makedirs(path)

		if os.path.exists(os.path.join(path, filename)):
			raise ValueError(f"A file with the name {filename} already exists.")

		with open(os.path.join(path, filename), 'w', encoding= 'utf-8') as f:
			f.write(text)

		# We are done writing, now let's make an entry in the index table.
		index = os.path.join('writings', 'index.html')
		with open(index , 'r', encoding = 'utf-8') as file:
			lines = file.read().split('\n')

		start = len(lines) - 4; end = start + 1
		fmtdate = "/".join(date.split('/')[::-1]) if date else 'undated'
		line = f'<li class="has-line-data" data-line-start="{start}" data-line-end="{end}">{date or "Undated"}' \
			 f'- <a href=\"/writings/{fmtdate}/{filename}\">{title}</a></li>'
		lines.insert(-2, line)
		html = '\n'.join(lines)

		with open(index, 'w', encoding = 'utf-8') as file:
			file.write(html)

		return print('👍')

def main():
	parser = clicore.Parser()
	parser.load_module(WritingUtils())
	parser.run()

if __name__ == '__main__':
	main()
	
