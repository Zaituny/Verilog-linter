

module test3 (//working example 
input  wire        button_0 , button_1 ,
input  wire        rst,
input  wire        clock,
output reg         unlock
);



localparam [2:0]    IDLE = 3'b000,
                     S1 = 3'b001,
                     S11 = 3'b011,
					 S011 = 3'b010,
					 S110 = 3'b110,
					 UNLOCK = 3'b111 ;
					 
reg [2:0]         current_state = IDLE,
                     next_state = IDLE;
		
// state transition 		
always @(posedge clock or negedge rst)
 begin
  if(!rst)
   begin
     current_state <= IDLE ;
   end
  else
   begin
     current_state <= next_state ;
   end
 end
 
// next_state logic
always @(*)
 begin
  case(current_state)
  IDLE     : begin
              if(button_0)
			   next_state = IDLE ;
			  else if (button_1)
               next_state = S1 ;
              else
               next_state = IDLE ;			  
             end
  S1       : begin
              if(button_0)
			   next_state = IDLE ;
			  else if (button_1)
               next_state = S11 ;
              else
               next_state = S1 ;	   
            end
  S11     : begin
              if(button_0)
			   next_state = S011 ;
			  else if (button_1)
               next_state = IDLE ;
              else
               next_state = S11 ;	    
            end
  S011    : begin
              if(button_0)
			   next_state = IDLE ;
			  else if (button_1)
               next_state = S110 ;
              else
               next_state = S011 ;	    
            end
  S110   : begin
             if(button_0)
			   next_state = UNLOCK ;
		     else if (button_1)
               next_state = IDLE ;
             else
               next_state = S110 ;	   
            end
				
  UNLOCK  : begin
               next_state = IDLE ;
            end	
  default :   next_state = IDLE ;		 
  
  endcase
end	


// next_state logic
always @(*)
 begin
  case(current_state)
  IDLE     : begin
              unlock   =  1'b0 ;		  
             end
  S1       : begin
              unlock   =  1'b0 ;
             end	
  S11      : begin
              unlock   =  1'b0 ;	   
             end
  S011     : begin
              unlock   =  1'b0 ;	   
             end
  S110    : begin
              unlock   =  1'b0 ;		   
             end		 
  UNLOCK   : begin
              unlock   =  1'b1 ;	
             end	
  default  : begin
              unlock   =  1'b0 ;
             end			  
  endcase
 end	
		
		
endmodule					 