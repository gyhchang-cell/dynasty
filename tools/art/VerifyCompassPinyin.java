import me.towdium.pinin.PinIn;
/** Uses the exact bundled JECharacters pinyin implementation without launching a user world. */
public class VerifyCompassPinyin {
 public static void main(String[] args) {
  PinIn p=new PinIn();
  for(String name:new String[]{"自然指南针","探险者指南针"})for(String query:new String[]{"zhinan","zhinanzhen","znz"}) {
   if(!p.contains(name,query))throw new AssertionError(name+" does not match "+query);
   System.out.println(name+" -> "+query+": PASS");
  }
  for(String[] pair:new String[][]{{"自然指南针","ziran"},{"探险者指南针","tanxian"}})
   if(!p.contains(pair[0],pair[1]))throw new AssertionError(pair[1]);
 }
}
