SELECT  count_ AS num_pkgs_maintained, count(*) AS num_maintainers_meeting_a_count
FROM (
	SELECT maintainer, count(*) AS count_
	FROM detection_results
	GROUP BY maintainer ORDER BY count_
	)
GROUP BY num_pkgs_maintained;
