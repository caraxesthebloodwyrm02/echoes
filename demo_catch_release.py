#!/usr/bin/env python3
"""
Demo script showcasing the Catch and Release System for intelligent caching
Demonstrates quick cross-referencing, conversation continuity, and multi-level caching
"""

import os
import sys
import time
import json
from datetime import datetime

# Load environment variables
os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.abspath(__file__)))

try:
    from core_modules.catch_release_system import catch_release, CacheLevel, ContentType
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the Echoes project root")
    sys.exit(1)


def demo_basic_catch_release():
    """Demonstrate basic catch and release operations"""
    print("\n" + "=" * 70)
    print("🗂️ BASIC CATCH & RELEASE DEMO")
    print("=" * 70)

    print("\n📥 Catching different types of content:")

    # Catch various content types
    content_samples = [
        ("Python is a versatile programming language", ContentType.CONCEPT),
        ("OpenAI GPT-4 is a large language model", ContentType.ENTITY),
        ("Machine learning requires quality data", ContentType.CONVERSATION),
        ("Debugging is twice as hard as writing code", ContentType.CONTEXT),
    ]

    cache_keys = []

    for content, content_type in content_samples:
        key = catch_release.catch(
            content=content,
            content_type=content_type,
            cache_level=CacheLevel.SHORT_TERM,
            tags={"demo", content_type.value},
            importance=0.7,
        )
        cache_keys.append((key, content, content_type))
        print(f"  ✅ Caught {content_type.value}: {content}")
        print(f"     Key: {key}")

    print(f"\n📤 Releasing cached content:")

    for key, original_content, content_type in cache_keys:
        released = catch_release.release(key)
        if released:
            print(f"  ✅ Released: {released}")
            print(f"     Match: {'✓' if released == original_content else '✗'}")
        else:
            print(f"  ✗ Failed to release: {key}")

    # Show cache statistics
    stats = catch_release.get_cache_statistics()
    print(f"\n📊 Cache Statistics:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Overall hit rate: {stats['overall_hit_rate']:.1%}")


def demo_cross_reference():
    """Demonstrate cross-reference functionality"""
    print("\n" + "=" * 70)
    print("🔗 CROSS-REFERENCE DEMO")
    print("=" * 70)

    print("\n📥 Populating cache with related content:")

    # Add related content about AI/ML
    ai_content = [
        (
            "Artificial intelligence transforms industries through automation",
            ContentType.CONCEPT,
            {"ai", "automation"},
        ),
        (
            "Machine learning algorithms learn patterns from data",
            ContentType.CONCEPT,
            {"ml", "algorithms"},
        ),
        (
            "Neural networks mimic the human brain's structure",
            ContentType.CONCEPT,
            {"neural", "brain"},
        ),
        (
            "Deep learning uses multiple layers of neural networks",
            ContentType.CONCEPT,
            {"deep", "learning"},
        ),
        (
            "OpenAI develops advanced AI models like GPT-4",
            ContentType.ENTITY,
            {"openai", "gpt"},
        ),
        (
            "Python is popular for AI development due to its libraries",
            ContentType.CONVERSATION,
            {"python", "ai"},
        ),
    ]

    keys = []
    for content, content_type, tags in ai_content:
        key = catch_release.catch(
            content=content,
            content_type=content_type,
            cache_level=CacheLevel.SHORT_TERM,
            tags=tags,
            importance=0.8,
        )
        keys.append(key)
        print(f"  ✅ Cached: {content[:50]}...")

    print(f"\n🔍 Performing cross-reference searches:")

    queries = [
        "artificial intelligence",
        "neural networks",
        "Python AI development",
        "OpenAI models",
    ]

    for query in queries:
        results = catch_release.cross_reference(query, max_results=3)

        print(f"\n  Query: '{query}'")
        if results:
            for i, result in enumerate(results, 1):
                print(f"    {i}. Relevance: {result.relevance_score:.1%}")
                print(f"       Content: {result.content}")
                print(f"       Type: {result.context_info['type']}")
                print(f"       Confidence: {result.confidence:.1%}")
        else:
            print("    No results found")


def demo_conversation_continuity():
    """Demonstrate conversation continuity tracking"""
    print("\n" + "=" * 70)
    print("🔄 CONVERSATION CONTINUITY DEMO")
    print("=" * 70)

    print("\n💬 Simulating conversation flow:")

    # Simulate a conversation about web development
    conversation = [
        ("I want to learn web development", "user", {"web", "development", "learning"}),
        (
            "Start with HTML, CSS, and JavaScript fundamentals",
            "assistant",
            {"html", "css", "javascript"},
        ),
        (
            "What framework should I learn after JavaScript?",
            "user",
            {"javascript", "framework", "question"},
        ),
        (
            "React is popular for building user interfaces",
            "assistant",
            {"react", "ui", "framework"},
        ),
        (
            "How about backend development?",
            "user",
            {"backend", "development", "question"},
        ),
        (
            "Node.js lets you use JavaScript for backend",
            "assistant",
            {"nodejs", "backend", "javascript"},
        ),
    ]

    session_id = f"demo_session_{int(time.time())}"
    conv_keys = []

    for message, role, tags in conversation:
        context = {
            "message": message,
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
        }

        key = catch_release.catch(
            content=context,
            content_type=ContentType.CONVERSATION,
            cache_level=CacheLevel.SESSION,
            tags=tags.union({role}),
            importance=0.7,
        )

        conv_keys.append(key)
        print(f"  {role.title()}: {message}")
        print(f"    Cached: {key}")

        # Create relationships between consecutive messages
        if len(conv_keys) > 1:
            catch_release.create_relationship(
                conv_keys[-2], conv_keys[-1], strength=0.9
            )

    print(f"\n🔗 Analyzing conversation continuity:")

    continuity = catch_release.get_conversation_continuity(session_id)

    print(f"  Session ID: {continuity['session_id']}")
    print(f"  Recent entries: {continuity['total_recent']}")
    print(f"  Continuity score: {continuity['continuity_score']:.1%}")

    if continuity["recent_entries"]:
        print(f"\n  Recent conversation flow:")
        for i, entry in enumerate(continuity["recent_entries"], 1):
            created = datetime.fromisoformat(entry["created_at"])
            time_ago = datetime.now() - created
            print(f"    {i}. {time_ago.seconds}s ago: {entry['content']['message']}")
            print(f"       Role: {entry['content']['role']}")
            print(f"       Tags: {', '.join(entry['tags'])}")


def demo_multi_level_caching():
    """Demonstrate different cache levels"""
    print("\n" + "=" * 70)
    print("📊 MULTI-LEVEL CACHING DEMO")
    print("=" * 70)

    print("\n🗂️ Testing different cache levels:")

    content = "This is a test message for multi-level caching"

    # Cache at different levels
    level_tests = [
        (CacheLevel.SESSION, "session", 1),
        (CacheLevel.SHORT_TERM, "short_term", 24),
        (CacheLevel.LONG_TERM, "long_term", 168),
        (CacheLevel.PERMANENT, "permanent", None),
    ]

    keys = {}
    for level, level_name, ttl_hours in level_tests:
        key = catch_release.catch(
            content=f"{content} ({level_name})",
            content_type=ContentType.CONCEPT,
            cache_level=level,
            tags={level_name, "test"},
            importance=0.6,
            ttl_hours=ttl_hours,
        )
        keys[level] = key
        print(f"  ✅ Cached at {level_name}: {key}")
        print(f"     TTL: {ttl_hours} hours" if ttl_hours else "     TTL: Permanent")

    print(f"\n📊 Cache breakdown by level:")

    stats = catch_release.get_cache_statistics()
    for cache_name, cache_stats in stats["cache_breakdown"].items():
        print(f"  {cache_name}:")
        print(f"    Size: {cache_stats['size']}/{cache_stats['max_size']}")
        print(f"    Hit rate: {cache_stats['hit_rate']:.1%}")
        print(f"    Hits: {cache_stats['hits']}")
        print(f"    Misses: {cache_stats['misses']}")


def demo_relationship_tracking():
    """Demonstrate relationship tracking between cached items"""
    print("\n" + "=" * 70)
    print("🔗 RELATIONSHIP TRACKING DEMO")
    print("=" * 70)

    print("\n🔗 Creating related content network:")

    # Create a knowledge graph about programming
    concepts = [
        ("Programming is the art of instructing computers", "programming"),
        ("Python is a beginner-friendly programming language", "python"),
        ("JavaScript powers interactive web applications", "javascript"),
        ("React is a JavaScript library for UI development", "react"),
        ("Node.js enables server-side JavaScript", "nodejs"),
    ]

    keys = {}
    for content, concept in concepts:
        key = catch_release.catch(
            content=content,
            content_type=ContentType.CONCEPT,
            cache_level=CacheLevel.SHORT_TERM,
            tags={concept, "programming"},
            importance=0.8,
        )
        keys[concept] = key
        print(f"  ✅ {concept.title()}: {content}")

    print(f"\n🔗 Creating relationships:")

    # Create relationships
    relationships = [
        ("programming", "python", 0.9),
        ("programming", "javascript", 0.9),
        ("javascript", "react", 0.8),
        ("javascript", "nodejs", 0.8),
        ("python", "nodejs", 0.6),  # Cross-language relationship
    ]

    for from_concept, to_concept, strength in relationships:
        catch_release.create_relationship(
            keys[from_concept], keys[to_concept], strength
        )
        print(f"  🔗 {from_concept} → {to_concept} (strength: {strength})")

    print(f"\n🔍 Finding related content:")

    # Find related content for Python
    python_key = keys["python"]
    related = catch_release.find_related(python_key, max_depth=2)

    print(f"\n  Content related to Python:")
    for i, result in enumerate(related, 1):
        print(f"    {i}. Relevance: {result.relevance_score:.1%}")
        print(f"       Depth: {result.context_info.get('depth', 0)}")
        print(f"       Content: {result.content}")


def demo_performance_optimization():
    """Demonstrate performance optimization features"""
    print("\n" + "=" * 70)
    print("⚡ PERFORMANCE OPTIMIZATION DEMO")
    print("=" * 70)

    print("\n📈 Performance testing with bulk operations:")

    # Bulk catch operation
    start_time = time.time()

    bulk_content = [f"Test message {i} for performance testing" for i in range(100)]

    keys = []
    for i, content in enumerate(bulk_content):
        key = catch_release.catch(
            content=content,
            content_type=ContentType.CONCEPT,
            cache_level=CacheLevel.SHORT_TERM,
            tags={"performance", "test"},
            importance=0.5,
        )
        keys.append(key)

    catch_time = time.time() - start_time

    print(f"  ✅ Cached {len(bulk_content)} items in {catch_time:.3f}s")
    print(f"  Rate: {len(bulk_content)/catch_time:.0f} items/second")

    # Bulk release operation
    start_time = time.time()

    successful_releases = 0
    for key in keys[:50]:  # Test first 50
        content = catch_release.release(key)
        if content:
            successful_releases += 1

    release_time = time.time() - start_time

    print(f"  ✅ Released {successful_releases}/50 items in {release_time:.3f}s")
    print(f"  Rate: {successful_releases/release_time:.0f} items/second")

    # Cross-reference performance
    start_time = time.time()

    results = catch_release.cross_reference("test message", max_results=10)

    xref_time = time.time() - start_time

    print(f"  ✅ Cross-reference found {len(results)} results in {xref_time:.3f}s")

    # Show final statistics
    stats = catch_release.get_cache_statistics()
    print(f"\n📊 Final Performance Statistics:")
    print(f"  Total catches: {stats['operations']['total_catches']}")
    print(f"  Total releases: {stats['operations']['total_releases']}")
    print(f"  Cross-references: {stats['operations']['cross_references']}")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Cache misses: {stats['cache_misses']}")
    print(f"  Overall hit rate: {stats['overall_hit_rate']:.1%}")


def demo_export_import():
    """Demonstrate export and import functionality"""
    print("\n" + "=" * 70)
    print("💾 EXPORT & IMPORT DEMO")
    print("=" * 70)

    print("\n📤 Exporting cache contents:")

    # Add some sample content
    sample_data = [
        ("Machine learning algorithms learn from data", ContentType.CONCEPT),
        ("Python is excellent for data science", ContentType.CONVERSATION),
        ("TensorFlow is a popular ML framework", ContentType.ENTITY),
    ]

    for content, content_type in sample_data:
        catch_release.catch(
            content=content,
            content_type=content_type,
            cache_level=CacheLevel.SHORT_TERM,
            tags={"export", "demo"},
            importance=0.7,
        )

    # Export cache
    export_file = f"cache_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    catch_release.export_cache(export_file)

    print(f"  ✅ Exported cache to: {export_file}")

    # Check file size
    if os.path.exists(export_file):
        file_size = os.path.getsize(export_file)
        print(f"  File size: {file_size:,} bytes")

        # Show sample content
        with open(export_file, "r") as f:
            data = json.load(f)

        print(f"  Exported entries: {len(data['entries'])}")
        print(f"  Export timestamp: {data['export_timestamp']}")

        print(f"\n📄 Sample exported entry:")
        if data["entries"]:
            sample = data["entries"][0]
            print(f"    Key: {sample['key']}")
            print(f"    Type: {sample['content_type']}")
            print(f"    Level: {sample['cache_level']}")
            print(f"    Content: {str(sample['content'])[:50]}...")
            print(f"    Tags: {list(sample['tags'])}")


def main():
    """Run all catch and release demos"""
    print("\n✨ Welcome to the Catch & Release System Demo!")
    print(
        "This showcases intelligent caching for quick cross-referencing and conversation continuity."
    )

    # Run all demos
    demo_basic_catch_release()
    demo_cross_reference()
    demo_conversation_continuity()
    demo_multi_level_caching()
    demo_relationship_tracking()
    demo_performance_optimization()
    demo_export_import()

    print("\n" + "=" * 70)
    print("🎉 Catch & Release System Demo Complete!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ Multi-level caching (session/short/long/permanent)")
    print("  ✅ Intelligent cross-referencing with relevance scoring")
    print("  ✅ Conversation continuity tracking")
    print("  ✅ Relationship graph between cached items")
    print("  ✅ High-performance bulk operations")
    print("  ✅ Thread-safe LRU cache implementation")
    print("  ✅ Automatic expiration and cleanup")
    print("  ✅ Export/import functionality")
    print("  ✅ Comprehensive indexing (entities, concepts, tags, temporal)")

    print("\nCache Levels:")
    print("  Session: Current session only")
    print("  Short-term: Few hours of retention")
    print("  Long-term: Days to weeks")
    print("  Permanent: Until manually cleared")

    print("\nContent Types:")
    print("  Conversation, Entity, Concept, Thought Chain")
    print("  Cross Reference, Context, Response, Pattern")

    print("\nTry the interactive mode with:")
    print("  python assistant_v2_core.py")
    print("  Then try commands like:")
    print("    cache                  - Show cache statistics")
    print("    xref <query>           - Quick cross-reference lookup")
    print("    continuity             - Show conversation continuity")
    print("    catch <content>        - Manually cache content")
    print("    release <key>          - Retrieve cached content")
    print("    clearcache <level>     - Clear specific cache level")


if __name__ == "__main__":
    main()
