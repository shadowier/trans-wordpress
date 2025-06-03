from bs4 import BeautifulSoup, Comment, NavigableString
import sys

def is_translatable_text(element):
    # Helper to identify text nodes that should be translated
    if isinstance(element, Comment):
        return False
    current = element.parent
    while current:
        if current.name in ['script', 'style']:
            return False
        current = current.parent

    if isinstance(element, NavigableString) and element.string.strip():
        return True
    return False

def get_all_translatable_text_nodes(target_element):
    text_nodes = []
    for descendant in target_element.descendants:
        if is_translatable_text(descendant):
            text_nodes.append(descendant)
    return text_nodes

# Read HTML content from the copied file to modify it
try:
    with open('SE2_zh.html', 'r', encoding='utf-8') as f:
        html_to_modify_content = f.read()
except FileNotFoundError:
    print("Error: SE2_zh.html not found.")
    sys.exit(1)

# Read translated text
try:
    with open('translated_content.txt', 'r', encoding='utf-8') as f:
        translated_lines_from_file = [line.strip() for line in f.readlines()]
except FileNotFoundError:
    print("Error: translated_content.txt not found.")
    sys.exit(1)

soup = BeautifulSoup(html_to_modify_content, 'html.parser')

# Attempt to update lang attribute (it's known this might fail for SE2.html)
html_tag = soup.find('html')
if html_tag:
    html_tag['lang'] = 'zh'
else:
    # This is expected for SE2.html as it doesn't have a root <html> tag.
    # We can create one to wrap the content if absolutely necessary,
    # but for now, we'll just note it.
    print("Warning: Root <html> tag not found. Could not set lang attribute. The document might be a fragment.")
    # Optionally, create and wrap if it's truly missing and desired
    # if not soup.contents or soup.contents[0].name != 'html':
    #     current_root = soup.contents[0] if soup.contents else None
    #     html_tag_new = soup.new_tag('html', lang='zh')
    #     if current_root:
    #         current_root.wrap(html_tag_new)
    #     else: # If soup is empty for some reason
    #         soup.append(html_tag_new)
    #     html_tag = html_tag_new # update reference
    #     print("Info: Wrapped content in a new <html> tag and set lang='zh'.")


# Find the main content div in the soup we are modifying
main_content_div_to_modify = soup.find('div', class_='elementor-kit-272 elementor-page elementor-page-1744')

if main_content_div_to_modify:
    # Get all translatable text nodes from the div we are going to modify
    target_text_nodes_in_soup = get_all_translatable_text_nodes(main_content_div_to_modify)

    num_nodes_to_replace = len(target_text_nodes_in_soup)
    num_translated_lines = len(translated_lines_from_file)

    if num_nodes_to_replace != num_translated_lines:
        print(f"Warning: Mismatch in number of translatable text nodes ({num_nodes_to_replace}) and available translated lines ({num_translated_lines}).")
        # Adjust the number of lines to use, preferring the count of actual nodes
        # This means if translated_lines_from_file is longer, extra lines will be ignored.
        # If shorter, replacement will be incomplete (as handled by StopIteration later).

    translated_lines_iter = iter(translated_lines_from_file)

    for i, node in enumerate(target_text_nodes_in_soup):
        try:
            translated_line = next(translated_lines_iter)
            node.string.replace_with(translated_line)
        except StopIteration:
            print(f"Warning: Ran out of translated lines at node index {i}. {num_nodes_to_replace - i} nodes remain untranslated.")
            break
        except Exception as e:
            print(f"Error replacing text for node {i} ('{str(node)[:30]}...'): {e}")

    # Write the modified HTML to SE2_zh.html
    try:
        with open('SE2_zh.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"Successfully updated SE2_zh.html with 'translated' content.")
    except Exception as e:
        print(f"Error writing to SE2_zh.html: {e}")
else:
    print("Error: Main content div 'div.elementor-kit-272.elementor-page.elementor-page-1744' not found in SE2_zh.html.")
    # If the main div isn't found, but we tried to add/modify an <html> tag, save that.
    if html_tag and html_tag.get('lang') == 'zh':
         try:
            with open('SE2_zh.html', 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            print("Warning: Main content div not found, but SE2_zh.html was saved (likely only with lang attribute change if successful, or original content if not).")
         except Exception as e:
            print(f"Error writing to SE2_zh.html even after main div not found: {e}")
