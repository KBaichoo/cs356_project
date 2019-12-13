select
    shared_ptr + unique_ptr + scoped_ptr + weak_ptr + intrusive_ptr as smart_ptr_usage
from (
     select
        [detection_tool_output.shared_ptr.occurrences] as shared_ptr,
        [detection_tool_output.unique_ptr.occurrences] as unique_ptr,
        [detection_tool_output.scoped_ptr.occurrences] as scoped_ptr,
        [detection_tool_output.weak_ptr.occurrences] as weak_ptr,
        [detection_tool_output.intrusive_ptr.occurrences] as intrusive_ptr
     from detection_results
)
where smart_ptr_usage < 2000 and smart_ptr_usage > 40;
