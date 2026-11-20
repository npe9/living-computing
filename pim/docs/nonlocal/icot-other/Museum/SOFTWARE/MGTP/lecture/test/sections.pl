# LaTeX2HTML 96.1 (Feb 5, 1996)
# Associate sections original text with physical files.

$key = q/0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0/;
$section_info{$key} = '0%:%test.html%:%ÌµÂê' unless ($section_info{$key}); 
$done{"test.html"} = 1;
$key = q/0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0/;
$section_info{$key} = '3%:%node1.html%:%node1.html' unless ($section_info{$key}); 
$done{"node1.html"} = 1;

1;

