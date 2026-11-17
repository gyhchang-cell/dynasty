import com.dynasty.sweepqa.CaseLog;
import java.util.*;
public class CaseLogCheck {
 static int checks;
 static void ok(boolean b){if(!b)throw new AssertionError("check "+checks);checks++;}
 static void rejected(Runnable r){boolean rejected=false;try{r.run();}catch(IllegalStateException ex){rejected=true;}ok(rejected);}
 public static void main(String[] args){
  var client=new CaseLog("client");var server=new CaseLog("server");
  server.begin("first","nonce-a","success");client.begin("first","nonce-a","success");
  client.event("attack",Map.of("target","main-a"));client.event("end",Map.of("ticks",40));
  var old=client.snapshot();var oldStamp=client.stamp();ok(old.size()==2);ok(oldStamp.get("role").equals("client"));
  rejected(()->client.begin("third","nonce-b","success"));
  client.close();client.event("late-after-window",Map.of());ok(client.snapshot().size()==2);
  ok(server.current().equals("first")); // Remote clear cannot be necessary to release client.
  client.begin("third","nonce-b","success");client.event("attack",Map.of("target","main-b"));
  ok(client.snapshot().size()==1);ok(old.size()==2);ok(old.get(0).get("case").equals("first"));
  ok(client.snapshot().get(0).get("case").equals("third"));
  ok(!client.stamp().get("capture").equals(oldStamp.get("capture")));ok(client.stamp().get("binding").equals("nonce-b"));
  ok(server.current().equals("first"));server.close();ok(client.current().equals("third"));
  client.close();rejected(()->client.begin("first","nonce-c","invulnerable"));
  rejected(()->client.begin("../bad","nonce-c","invulnerable"));rejected(()->client.begin("bad","","success"));
  client.begin("negative","nonce-c","invulnerable");client.event("negative",Map.of());
  ok(client.snapshot().size()==1);ok(client.stamp().get("mode").equals("invulnerable"));
  var result=new TreeMap<String,Object>(client.stamp());result.put("checks",checks);System.out.println(result);
 }
}
