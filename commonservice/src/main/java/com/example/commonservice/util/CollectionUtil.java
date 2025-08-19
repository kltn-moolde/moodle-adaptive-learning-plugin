package com.example.commonservice.util;

import java.util.*;
import java.util.stream.Collectors;

public class CollectionUtil {
    
    /**
     * Check if two collections have same elements (regardless of order)
     */
    public static <T> boolean haveSameElements(Collection<T> col1, Collection<T> col2) {
        if (col1 == null && col2 == null) return true;
        if (col1 == null || col2 == null) return false;
        if (col1.size() != col2.size()) return false;
        
        return new HashSet<>(col1).equals(new HashSet<>(col2));
    }
    
    /**
     * Get intersection of two collections
     */
    public static <T> Set<T> intersection(Collection<T> col1, Collection<T> col2) {
        if (ValidationUtil.isEmpty(col1) || ValidationUtil.isEmpty(col2)) {
            return new HashSet<>();
        }
        
        return col1.stream()
                .filter(col2::contains)
                .collect(Collectors.toSet());
    }
    
    /**
     * Get union of two collections
     */
    public static <T> Set<T> union(Collection<T> col1, Collection<T> col2) {
        Set<T> result = new HashSet<>();
        if (ValidationUtil.isNotEmpty(col1)) result.addAll(col1);
        if (ValidationUtil.isNotEmpty(col2)) result.addAll(col2);
        return result;
    }
    
    /**
     * Get difference between two collections (elements in col1 but not in col2)
     */
    public static <T> Set<T> difference(Collection<T> col1, Collection<T> col2) {
        if (ValidationUtil.isEmpty(col1)) return new HashSet<>();
        if (ValidationUtil.isEmpty(col2)) return new HashSet<>(col1);
        
        return col1.stream()
                .filter(item -> !col2.contains(item))
                .collect(Collectors.toSet());
    }
    
    /**
     * Partition list into smaller lists of specified size
     */
    public static <T> List<List<T>> partition(List<T> list, int size) {
        if (ValidationUtil.isEmpty(list) || size <= 0) {
            return new ArrayList<>();
        }
        
        List<List<T>> partitions = new ArrayList<>();
        for (int i = 0; i < list.size(); i += size) {
            partitions.add(list.subList(i, Math.min(i + size, list.size())));
        }
        return partitions;
    }
    
    /**
     * Get random element from collection
     */
    public static <T> T getRandomElement(Collection<T> collection) {
        if (ValidationUtil.isEmpty(collection)) return null;
        
        List<T> list = new ArrayList<>(collection);
        Random random = new Random();
        return list.get(random.nextInt(list.size()));
    }
    
    /**
     * Get n random elements from collection
     */
    public static <T> List<T> getRandomElements(Collection<T> collection, int n) {
        if (ValidationUtil.isEmpty(collection) || n <= 0) {
            return new ArrayList<>();
        }
        
        List<T> list = new ArrayList<>(collection);
        Collections.shuffle(list);
        return list.subList(0, Math.min(n, list.size()));
    }
    
    /**
     * Remove duplicates from list while preserving order
     */
    public static <T> List<T> removeDuplicates(List<T> list) {
        if (ValidationUtil.isEmpty(list)) return new ArrayList<>();
        
        return list.stream()
                .distinct()
                .collect(Collectors.toList());
    }
    
    /**
     * Find most frequent element in collection
     */
    public static <T> T getMostFrequent(Collection<T> collection) {
        if (ValidationUtil.isEmpty(collection)) return null;
        
        Map<T, Long> frequencyMap = collection.stream()
                .collect(Collectors.groupingBy(item -> item, Collectors.counting()));
        
        return frequencyMap.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(null);
    }
    
    /**
     * Convert array to list safely
     */
    @SafeVarargs
    public static <T> List<T> toList(T... items) {
        if (items == null) return new ArrayList<>();
        return Arrays.asList(items);
    }
    
    /**
     * Create map from alternating key-value arguments
     */
    @SuppressWarnings("unchecked")
    public static <K, V> Map<K, V> createMap(Object... keyValuePairs) {
        if (keyValuePairs.length % 2 != 0) {
            throw new IllegalArgumentException("Number of arguments must be even (key-value pairs)");
        }
        
        Map<K, V> map = new HashMap<>();
        for (int i = 0; i < keyValuePairs.length; i += 2) {
            map.put((K) keyValuePairs[i], (V) keyValuePairs[i + 1]);
        }
        return map;
    }
    
    /**
     * Filter collection by predicate
     */
    public static <T> List<T> filter(Collection<T> collection, java.util.function.Predicate<T> predicate) {
        if (ValidationUtil.isEmpty(collection)) return new ArrayList<>();
        
        return collection.stream()
                .filter(predicate)
                .collect(Collectors.toList());
    }
}
