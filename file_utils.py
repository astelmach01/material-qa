from os import PathLike

import jinja2

def hydrated_markdown_section_contents(file_path: PathLike, heading_name: str,
									   **kwargs) -> str:
	"""
	Extracts a specific H1 section from a Markdown file and hydrates it
	using Jinja2 templating.

	Args:
		file_path: The path to the Markdown file.
		heading_name: The name of the H1 heading (without the '#').
		**kwargs: Keyword arguments to use as context for Jinja2 rendering.

	Returns:
		A string containing the hydrated content of the specified section.
		Returns an empty string if the heading is not found.

	Raises:
		FileNotFoundError: If the file at file_path does not exist.
		jinja2.exceptions.TemplateError: If there is an issue with the template rendering.
	"""
	with open(file_path, 'r', encoding='utf-8') as f:
		lines = f.readlines()

	content_lines = []
	in_section = False

	for line in lines:
		# Check if we've found the start of the target section
		if line.strip() == f'# {heading_name}':
			in_section = True
			continue

		# If we are in the target section, collect the content
		if in_section:
			# Stop if we encounter the next H1 heading
			if line.startswith('# '):
				break
			content_lines.append(line)

	raw_content = "".join(content_lines).strip()

	if not raw_content:
		return ""

	# Hydrate the content using Jinja2
	template = jinja2.Template(raw_content)
	hydrated_content = template.render(**kwargs)

	return hydrated_content
