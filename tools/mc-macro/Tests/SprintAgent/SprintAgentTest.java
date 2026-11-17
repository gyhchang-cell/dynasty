package local.mcmacro;
import java.lang.instrument.Instrumentation;
import java.lang.reflect.Proxy;
import java.util.*;
public final class SprintAgentTest {
 static int tests=0;
 static void check(boolean b){tests++;if(!b)throw new AssertionError("check "+tests);}
 static class ObfuscatedKey {static Map<String,ObfuscatedKey> z=new HashMap<>();String x="key.sprint";boolean y;int count;}
 static class ToggleKey extends ObfuscatedKey {java.util.function.BooleanSupplier toggle=()->true;}
 static class BadKey extends ObfuscatedKey {boolean ambiguous;}
 static class BadToggle extends ToggleKey {java.util.function.BooleanSupplier second=()->false;}
 static class Options {ObfuscatedKey sprint;}
 static class Client implements java.util.concurrent.Executor {
  static Client instance=new Client();Options options=new Options();
  public void execute(Runnable task){task.run();}
 }
 static Instrumentation instrumentation(Class<?>...classes){return (Instrumentation)Proxy.newProxyInstance(SprintAgentTest.class.getClassLoader(),new Class<?>[]{Instrumentation.class},(p,m,a)->m.getName().equals("getAllLoadedClasses")?classes:null);}
 public static void main(String[]args)throws Exception{
  ObfuscatedKey key=new ObfuscatedKey();ObfuscatedKey.z.put("key.sprint",key);
  check(SprintAgent.find(instrumentation(ObfuscatedKey.class))==key);
  check(!SprintAgent.downField(key).getBoolean(key));key.y=true;
  check(SprintAgent.downField(key).getBoolean(key));
  ToggleKey toggle=new ToggleKey();toggle.y=true;
  check(SprintAgent.downField(toggle).getBoolean(toggle));
  check(SprintAgent.toggle(toggle));
  check(!SprintAgent.toggle(key));
  toggle.toggle=()->false;check(!SprintAgent.toggle(toggle));
  try{SprintAgent.toggle(new BadToggle());throw new AssertionError();}catch(IllegalStateException expected){tests++;}
  check(SprintAgent.executor(instrumentation(Options.class,Client.class),key)==Client.instance);
  try{SprintAgent.executor(instrumentation(Options.class),key);throw new AssertionError();}catch(IllegalStateException expected){tests++;}
  try{SprintAgent.downField(new BadKey());throw new AssertionError();}catch(IllegalStateException expected){tests++;}
  ObfuscatedKey.z.clear();try{SprintAgent.find(instrumentation(ObfuscatedKey.class));throw new AssertionError();}catch(IllegalStateException expected){tests++;}
  System.out.println("Sprint agent checks "+tests+", failed 0");
 }
}
