package com.dynasty.sweepqa;

import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** JDK-only per-role lifecycle. Each process/session and loaded QA artifact are identified independently. */
public final class CaseLog {
 public static final String BUILD="sweepqa-02";
 private static final String SESSION=UUID.randomUUID().toString();
 private static String ARTIFACT="UNPACKAGED-OFFLINE";
 private static boolean sealed;
 public static synchronized void installArtifact(Path file){if(sealed)throw new IllegalStateException("Artifact identity already in use");ARTIFACT=Files.isRegularFile(file)?sha(file):"UNPACKAGED-OFFLINE";}
 private final String role;
 private final Set<String> used=new HashSet<>();
 private final List<Map<String,Object>> records=new ArrayList<>();
 private String current="",binding="",mode="",capture="";
 public CaseLog(String role){this.role=role;}
 public synchronized void begin(String id,String nonce,String which){
  if(!current.isEmpty()||used.contains(id)||!id.matches("[a-zA-Z0-9_-]{1,70}")||nonce.isEmpty())throw new IllegalStateException("Case active/reused/invalid");
  sealed=true;used.add(id);records.clear();current=id;binding=nonce;mode=which;capture=UUID.randomUUID().toString();
 }
 public synchronized String current(){return current;}
 public synchronized Map<String,Object> stamp(){return Map.of("case",current,"binding",binding,"mode",mode,"capture",capture,"role",role,"session",SESSION,"artifact",ARTIFACT,"build",BUILD);}
 public synchronized void event(String kind,Object data){if(current.isEmpty())return;var row=new LinkedHashMap<String,Object>(stamp());row.put("kind",kind);row.put("nano",System.nanoTime());row.put("thread",Thread.currentThread().getName());row.put("data",data);records.add(row);}
 public synchronized List<Map<String,Object>> snapshot(){return List.copyOf(records);}
 public synchronized void close(){current="";}
 public static String sha(Path p){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(p)));}catch(Exception e){throw new IllegalStateException(e);}}
}
