import csv, sys, re, os
R = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'required') + '/'
W = re.compile(r'window|menu|sash|font|screen|bitmap|^as_(graphics|mouse_input|input|output|superior|single_select|multiple_select|multiple_column|scroll|markers|menu|menu_input|choice|on_off_menu|scrolling_menu|input_buffer|standard_io_window|turning_menu)$|^with_(border|label|margin|icon|superior_input_buffer|default_mouse|click_information|pmacs_window|shared_window|bell|key_select|two_labels|mouse_scroll|pane|cwi|no_execute_choice_item|character)$|notifier|editor|pmacs|yank|^labeled_|text_buffer|io_buffer|^standard_(input|output)_file$|icon|color|^display|cascade|^inferior|^superior|choice')
L = re.compile(r'librar|compiler|macro|^package|class_maker|operator_pool|esp_parser|esp_unparser|^version$|assert_utility|syntax_error|undefined_method|frozen_term|^fdd_|file_backup|catalog')
SH = re.compile(r'program|coordinator|debug|interpreter|inspector|^trace|^user|abort|^process$|login|shell|spy|stop_watch|^peek$|exception|^event$|^error$|failure|throw|call_counter|^world$|messenger|^as_event_handler$|^dbg_win')
out = {k: [] for k in 'WLSO'}
for r in csv.DictReader(open(R + 'classes.tsv'), delimiter='\t'):
    c = r['class']
    if c.startswith('{') or c == '<root>':
        continue
    k = 'S' if SH.search(c) else 'L' if L.search(c) else 'W' if W.search(c) else 'O'
    if 'editor' in c and 'debug' not in c and 'font' not in c:
        k = 'W'
    out[k].append((c, r['n_programs'], r['class_methods'], r['instance_methods'], r['evidence_tier']))
names = {'W': 'window', 'L': 'librarian', 'S': 'shell', 'O': 'other'}
for k, v in out.items():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'coverage') + '/partition_' + names[k] + '.tsv', 'w') as f:
        f.write('class\tn_programs\tclass_methods\tinstance_methods\ttier\n')
        for t in v:
            f.write('\t'.join(t) + '\n')
    print(names[k], len(v))
