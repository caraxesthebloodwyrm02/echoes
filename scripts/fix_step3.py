            extraction_data['extracted_components'][f'docs/{doc_file}'] = {
                'extraction_method': 'documentation_analysis',
                'content_length': len(content),
                'sections_found': doc_metadata['sections'],
                'code_blocks': doc_metadata['code_blocks'],
                'integrity_verified': True
            }
            print(f'   ✅ {doc_file} - {doc_metadata["sections"]} sections, {len(content)} chars')
