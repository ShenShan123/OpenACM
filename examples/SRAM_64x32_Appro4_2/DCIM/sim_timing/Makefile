.PHONY: com sim cov clean db debug

OUTPUT = dut
SIM_DIR = ./DCIM/sim_timing
ALL_DEFINE = +define+DUMP_VPD+NTC+RECREM
#LIB
LIB_FILE = ./DCIM/nangate45/NangateOpenCellLibrary.v


#Code converage command
CM = -cm line+cond+fsm+branch+tgl
CM_NAME = -cm_name $(OUTPUT)
CM_DIR = -cm_dir $(SIM_DIR)/$(OUTPUT).vdb

#vpd file name
VPD_NAME = +vpdfile+$(SIM_DIR)/$(OUTPUT).vpd

#Compile command
VCS = vcs +v2k -timescale=1ns/1ps					\
		-full64										\
		-debug_acc+all								\
		-debug_region+cell+encrypt					\
		-sverilog									\
		-v $(LIB_FILE)								\
		+sdfverbose									\
		$(CM)										\
		$(CM_NAME)									\
		$(CM_DIR)									\
		$(ALL_DEFINE)								\
		$(VPD_NAME)									\
		-o $(SIM_DIR)/$(OUTPUT)					\
		-l $(SIM_DIR)/compile.log								\
		+neg_tchk									
#nospecify
#compsdf
#+vcs+flush+all
#neg_tchk

#simulation command
SIM = $(SIM_DIR)/$(OUTPUT)							\
	  $(CM) $(CM_NAME) $(CM_DIR)					\
	  $(VPD_NAME)									\
	  $(ALL_DEFINE)									\
	  -l $(SIM_DIR)/$(OUTPUT).log
#+ntb_ramdom_seend_automatic
#start compile
com:
	$(VCS) -f $(SIM_DIR)/file_list.f 

#start simulation
sim:
	$(SIM)

#show the coverage
cov:
	dve -covdir $(SIM_DIR)/*.vdb &

debug:
	dve -vpd $(SIM_DIR)/$(OUTPUT).vpd &

#verdi debug
db:
	verdi -sv -f $(SIM_DIR)/file_list.f -ssf $(SIM_DIR)/$(OUTPUT).fsdb

#start clean
clean:
	rm -rf ./csrc $(SIM_DIR)/*.daidir $(SIM_DIR)/*.log $(SIM_DIR)/simv* $(SIM_DIR)/*.key $(SIM_DIR)/*.vpd ./DVEfiles $(SIM_DIR)/${OUTPUT} $(SIM_DIR)/*.vdb $(SIM_DIR)/*.fsdb $(SIM_DIR)/*.vcd $(SIM_DIR)/*.txt sdfAnnotateInfo *.log