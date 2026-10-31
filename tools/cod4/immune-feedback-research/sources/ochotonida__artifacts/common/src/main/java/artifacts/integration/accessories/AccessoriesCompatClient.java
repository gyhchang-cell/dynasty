package artifacts.integration.accessories;

import artifacts.equipment.client.EquipmentRenderingManager;

public class AccessoriesCompatClient {

    public static void setup() {
        EquipmentRenderingManager.register(new AccessoriesRenderingHandler());
    }
}
