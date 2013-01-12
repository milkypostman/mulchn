DELETE FROM question_tag WHERE tag_id IN (SELECT id FROM tag WHERE name='');
DELETE FROM tag WHERE name='';
