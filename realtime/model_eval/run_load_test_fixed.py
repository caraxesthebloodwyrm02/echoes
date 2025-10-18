# Print results
print(f"✅ Successful: {result.successful_requests}/{result.total_requests}")
print(f"🚫 Rate Limited: {result.rate_limited_requests}")
print(f"Throughput: {result.throughput_rps:.1f} RPS")
print(f"Avg Response Time: {result.avg_response_time:.2f}s")
