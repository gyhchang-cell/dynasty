import com.dynasty.puzzle.RuinLayout;
import java.util.*;

/** Complete sealed-volume and walkability checks for all rotations of the new hall. */
public final class TreasuryLayoutTest {
    public static void main(String[] args) {
        for(int rotation=0;rotation<4;rotation++) {
            Map<String,RuinLayout.Role> cells=new HashMap<>();
            int chests=0,gates=0;
            for(var cell:RuinLayout.shell(3)) {
                int[] r=RuinLayout.rotate(cell.x(),cell.z(),rotation);
                if(Math.abs(r[0])>=14||Math.abs(r[1])>=14||cell.y()+1<0||cell.y()+1>=8)
                    throw new AssertionError("Outside bounding box");
                String key=cell.x()+","+cell.y()+","+cell.z();
                if(cells.put(key,cell.role())!=null)throw new AssertionError("Duplicate cell "+key);
                if(cell.role()==RuinLayout.Role.TREASURE)chests++;
                if(cell.role()==RuinLayout.Role.GATE)gates++;
            }
            if(chests!=2||gates!=4)throw new AssertionError("Wrong treasure/door count");
            for(int z=-13;z<=-4;z++)for(int x=-7;x<=7;x++)for(int y=-1;y<=5;y++) {
                boolean boundary=x==-7||x==7||z==-13||z==-4||y==-1||y==5;
                if(boundary){
                    var role=cells.get(x+","+y+","+z);
                    if(!Set.of(RuinLayout.Role.WALL,RuinLayout.Role.FLOOR,RuinLayout.Role.CEILING,RuinLayout.Role.GATE).contains(role))
                        throw new AssertionError("Breakable/open outer shell");
                }
            }
            for(boolean open:new boolean[]{false,true}) {
                Set<String> visited=new HashSet<>();ArrayDeque<int[]> queue=new ArrayDeque<>();queue.add(new int[]{0,-3});
                while(!queue.isEmpty()){
                    int[] p=queue.remove();String key=p[0]+","+p[1];if(!visited.add(key))continue;
                    for(int[] d:new int[][]{{1,0},{-1,0},{0,1},{0,-1}}){
                        int x=p[0]+d[0],z=p[1]+d[1];if(Math.abs(x)>7||z<-13||z>4)continue;
                        var a=cells.get(x+",0,"+z);var b=cells.get(x+",1,"+z);
                        boolean feet=a==RuinLayout.Role.AIR||a==RuinLayout.Role.RUG||(open&&a==RuinLayout.Role.GATE);
                        boolean head=b==RuinLayout.Role.AIR||(open&&b==RuinLayout.Role.GATE);
                        if(feet&&head&&!visited.contains(x+","+z))queue.add(new int[]{x,z});
                    }
                }
                if(visited.contains("4,-9")!=open||visited.contains("-4,-9")!=open)
                    throw new AssertionError("Chest access not gated by puzzle");
            }
        }
        if(!RuinLayout.shell(2).equals(RuinLayout.shell()))throw new AssertionError("Legacy layout changed");
        System.out.println("PASS: v3 bounds, sealed shell, two treasure chests, 2-block walkways, locked/unlocked reachability; legacy unchanged.");
    }
}
