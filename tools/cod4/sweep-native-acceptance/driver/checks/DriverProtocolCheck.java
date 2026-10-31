import com.dynasty.sweepdriver.SweepStageDriver.Schedule;
import com.dynasty.sweepdriver.SweepStageDriver.RawImport;
import java.nio.file.*;
import java.util.*;
public class DriverProtocolCheck {
 static int checks;
 static void ok(boolean b){if(!b)throw new AssertionError("check="+checks);checks++;}
 interface Action{void run()throws Exception;}
 static void rejected(Action a)throws Exception{boolean failed=false;try{a.run();}catch(IllegalStateException|IllegalArgumentException|FileAlreadyExistsException ex){failed=true;}ok(failed);}
 public static void main(String[] args)throws Exception{
  for(int first=1;first<=6;first++)for(int third=1;third<=6;third++){
   var schedule=new Schedule("bounded-test");var ids=new HashSet<String>();var controls=new HashSet<String>();String fp="",tp="";int count=0;
   for(int v=0;v<2;v++)for(int attempt=1;attempt<=(v==0?first:third);attempt++){
    var c=schedule.next();String id=(String)c.get("case");ok(ids.add(id));ok(c.get("view").equals(v==0?"first":"third"));ok(c.get("mode").equals("success"));ok(c.get("calibration").equals(""));ok(((Integer)c.get("index"))==count++);
    boolean boundary=attempt==(v==0?first:third);schedule.finish(id,boundary);if(boundary){if(v==0)fp=id;else tp=id;}
   }
   for(int n=0;n<6;n++){var c=schedule.next();String id=(String)c.get("case"),view=(String)c.get("view");ok(ids.add(id));ok(controls.add(c.get("mode")+"/"+view));ok(c.get("calibration").equals(view.equals("first")?fp:tp));ok(((Integer)c.get("index"))==count++);schedule.finish(id,false);}
   ok(controls.equals(Set.of("cancel-attack/first","cancel-attack/third","cancel-damage/first","cancel-damage/third","invulnerable/first","invulnerable/third")));ok(count==first+third+6&&count<=18);ok(schedule.finished);rejected(()->schedule.next());
  }
  for(boolean failThird:List.of(false,true)){
   var s=new Schedule("no-boundary");if(failThird){var first=s.next();s.finish((String)first.get("case"),true);}
   for(int n=0;n<6;n++){var c=s.next();s.finish((String)c.get("case"),false);}int before=s.index;rejected(()->s.next());ok(before==s.index);ok(!s.finished&&s.negative==0);
  }
  var order=new Schedule("order");var a=order.next();rejected(()->order.next());rejected(()->order.finish("foreign-case",true));order.finish((String)a.get("case"),true);rejected(()->order.finish((String)a.get("case"),true));
  rejected(()->new Schedule("../bad"));
  Path root=Path.of(args[0]);Files.createDirectories(root);Path source=root.resolve("source.json"),dest=root.resolve("import.json");byte[] original="{\r\n  \"nonce\":\"原始字段\",\"order\":1\r\n}\n".getBytes(java.nio.charset.StandardCharsets.UTF_8);Files.write(source,original);
  RawImport.copy(source,dest);ok(Arrays.equals(original,Files.readAllBytes(dest)));ok(RawImport.sha(source).equals(RawImport.sha(dest)));RawImport.copy(source,dest);ok(Arrays.equals(original,Files.readAllBytes(dest)));
  Files.writeString(source,"DIFFERENT");rejected(()->RawImport.copy(source,dest));ok(Arrays.equals(original,Files.readAllBytes(dest)));
  Path stale=root.resolve("new.json");Files.writeString(root.resolve("new.json.import.tmp"),"stale-partial");rejected(()->RawImport.copy(source,stale));ok(!Files.exists(stale));RawImport.copy(dest,dest);ok(Arrays.equals(original,Files.readAllBytes(dest)));
  System.out.println("JDK_SCHEDULE_AND_RAW_IMPORT_PASS checks="+checks+"; no Minecraft or Forge runtime");
 }
}
